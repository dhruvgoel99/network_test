"""
    Module to test for network connectivity
    Test for different stats and pings
"""
import datetime
import logging
import re
import paramiko
import pytest
import pyeapi

import config

logging.basicConfig(level=logging.DEBUG)
mylogger = logging.getLogger()

OUTPUT_FILE = 'vm_details.txt'
TIMESTAMP = str(datetime.datetime.now())


class FixtureHelper:
    """Helper class for fixture"""
    def __init__(self, name, req):
        """Initialize hostname"""
        self.hostname = name
        self.req = req
        self.node = None

    def connection(self):
        """connecting to specified host"""
        self.node = pyeapi.connect_to(self.hostname)

    def api_req(self):
        """return the results for 'show' commands"""
        self.connection()
        return self.node.api(self.req)

    def execute_cmd(self):
        """return result for any other command"""
        self.connection()
        return self.node.execute([self.req])


@pytest.fixture(name="ini_command")
def pyeapi_connection(args):
    """ Connecting switch """
    return FixtureHelper(args[0], args[1])


class TestSimpleWidget:
    """
        Contain all test_cases for checking network state
    """
    out = None
    ssh = None

    # setup will run first
    def setup_method(self):
        """ SSH connect to the VM node """
        self.out = None
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        mylogger.info('Connecting to the Guest VM')
        self.ssh.connect(hostname=config.HOSTNAME, username=config.USERNAME,
                         password=config.PASSWORD, port=config.PORT)

    @pytest.mark.parametrize('args', [('S1', 'vlans'), ('Router', 'vlans')])
    def test_vlan(self, ini_command):
        """ Test for vlan available """
        # tmp = ini_command.connection().api('vlans')
        tmp = ini_command.api_req()
        out = [i['vlan_id'] for i in tmp]
        self.out = TIMESTAMP + ' VLANs: ' + str(len(out)) + '\n'
        assert 1 in out

    @pytest.mark.parametrize('args', [('S1', 'show mac address-table'),
                                      ('Router', 'show mac address-table')])
    def test_mac_address(self, ini_command):
        """Check number of mac address available in Switch"""
        tmp = ini_command.execute_cmd()
        out = [i['mac_address'] for i in tmp['result']]
        self.out = TIMESTAMP + ' MACs: ' + ' '.join(out) + '\n'
        assert 4 == len(out)

    @pytest.mark.parametrize('args', [('ROUTER1', 'show ip route'),
                                      ('ROUTER2', 'show ip route'),
                                      ('ROUTER3', 'show ip route')])
    def test_ip_route(self, ini_command):
        """Check for particular IP address available or not in route
            from particular Router"""
        tmp = ini_command.execute_cmd()
        assert len(re.findall(r"B\s+10.10.10.0", tmp['result'])) != 0

    @pytest.mark.parametrize('args', [('Router', 'show ip route')])
    def test_neighbours(self, ini_command):
        """test for number of neighbours of devices"""
        return ini_command.execute_cmd()

    @pytest.mark.parametrize('args', [('Router', 'show arp')])
    def test_arp(self, ini_command):
        """test number of devices reachable"""
        tmp = ini_command.execute_cmd()
        out = [i['Address'] for i in tmp['result']]
        self.out = TIMESTAMP + ' IPs: ' + ' '.join(out) + '\n'
        assert 6 == len(out)  # extra 2 for router interfaces

    # test cases goes here with 'test' prefix
    # run this marked testcase: (pytest -v -m "cli")
    # other test cases: (pytest -v -m "not cli")
    @pytest.mark.cli
    def test_cpu_num(self):
        """ Test for number of CPUs assigned to the VM"""
        _, stdout, __ = self.ssh.exec_command('lscpu | '
                                              'grep -e ^CPU\\(s\\)')
        mylogger.info('Get Number of CPUs from the VM')
        out = stdout.readline().split()
        self.out = TIMESTAMP + ' CPU_NUM: ' + out[-1] + '\n'
        assert out[-1] == '2'

    def test_mem_avail(self):
        """ Test for memory availability: More than 50% """
        _, stdout, __ = self.ssh.exec_command('free -m | grep Mem:')
        mylogger.warning('Memory availability')
        out = stdout.readline().split()
        self.out = TIMESTAMP + ' MEM_AVAIL: ' + out[-1] + '\n'
        assert int(out[-1]) >= 0.5 * int(out[1])

    @pytest.mark.parametrize("ip_address", ['192.168.234.129',
                                            '192.168.24.130',
                                            '192.168.1.42'])
    def test_ping(self, ip_address):
        """ Check the connectivity between host and diff VMs """
        _, stdout, __ = self.ssh.exec_command('ping -c 5 ' +
                                              ip_address)
        mylogger.warning('Ping')
        out = []
        while True:
            content = stdout.readline()
            if len(content) == 0:
                break
            out.append(content)
        res = re.findall("\\d*%", out[-2])
        self.out = TIMESTAMP + ' PING_Details for ' + ip_address + ': ' + \
            res[0] + ' Packet Loss\n'
        assert int(res[0][:-1]) <= 25

    def test_cpu_idle(self):
        """ Test for % CPU availability: More than 50"""
        _, stdout, __ = self.ssh.exec_command('sudo apt install '
                                              'sysstat; mpstat | '
                                              'grep -e .[0-9]$')
        mylogger.info('CPU Idle%')
        out = stdout.readline().split()
        self.out = TIMESTAMP + ' CPU_IDLE: ' + out[-1] + '\n'
        assert float(out[-1]) >= 50

    # this will run after the test cases
    def teardown_method(self):
        """ Write all the results to a file """
        with open(OUTPUT_FILE, "a", encoding="utf-8") as file:
            file.write(self.out)
        file.close()
        self.ssh.close()
