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

logging.basicConfig(level=logging.DEBUG)
mylogger = logging.getLogger()

OUTPUT_FILE = 'vm_details.txt'
TIMESTAMP = str(datetime.datetime.now())


@pytest.fixture
def ini_command():
    """ Connecting switch """
    node = pyeapi.connect_to('S1')
    _ = node.enable('show version')
    return node


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
        self.ssh.connect(hostname='192.168.234.129', username='dhruv',
                         password='root', port=22)

    def test_vlan(self):
        """ Test for vlan available """
        tmp = ini_command.api('vlans')
        out = [i['vlan_id'] for i in tmp]
        self.out = TIMESTAMP + ' VLANs: ' + str(len(out)) + '\n'
        assert 1 in out

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
