import paramiko


class ParamikoHelper():
    # self = ParamikoHelper(user_name)
    def __init__(self, ssh_username, remote_ip='106.14.45.82', ssh_password=''):
        remote_ssh_port = 22
        self.remote_ip = remote_ip
        self.remote_ssh_port = remote_ssh_port
        self.ssh_password = ssh_password
        self.ssh_username = ssh_username

    def connect_ssh(self):
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(hostname=self.remote_ip, port=self.remote_ssh_port, username=self.ssh_username,
                             password=self.ssh_password)
        except Exception as e:
            print(e)
        return self.ssh

    def close_ssh(self):
        try:
            self.ssh.close()
        except Exception as e:
            print(e)

    def exec_shell(self, shell, is_print=0):
        ssh = self.connect_ssh()
        try:
            stdin, stdout, stderr = ssh.exec_command(shell)
            out = []
            for x in stdout.readlines():
                if is_print == 1:
                    print(x.replace('\n', ''))
                out.append(x.replace('\n', ''))
            ssh.close()
            return out
        except Exception as e:
            print(e)

    def get_pid(self, service, user_name):
        out = self.exec_shell('ps -ef --sort=ruid| grep python')
        for x in out:
            if ('grep ' in x) | (x[:4] == 'root'):
                out.remove(x)
        pid = ''
        for x in out:
            if (service in x) & (user_name[:5] in x):
                for y in x.split(' ')[1:]:
                    if len(y) > 0:
                        pid = y
                        break
                    else:
                        pass
        return pid

    def sftp_put_file(self, local_dir, remote_dir):
        try:
            t = paramiko.Transport(self.remote_ip, self.remote_ssh_port)
            t.connect(username=self.ssh_username, password=self.ssh_password)
            sftp = paramiko.SFTPClient.from_transport(t)
            sftp.put(local_dir, remote_dir)
            t.close()
        except Exception as e:
            print(e)

    def sftp_get_file(self, local_dir, remote_dir):
        try:
            t = paramiko.Transport(self.remote_ip, self.remote_ssh_port)
            t.connect(username=self.ssh_username, password=self.ssh_password)
            sftp = paramiko.SFTPClient.from_transport(t)
            sftp.get(remote_dir, local_dir)
            t.close()
        except Exception as e:
            print(e)

    def invok_shell(self, shell):
        return self.ssh.invoke_shell(shell)


# 配置区
#################################################

def main(config, cmd):
    user_name = config['user_name']  # rubinstein pit_v2 pit_prd
    filter = config['filter']
    filter2 = config['filter2']
    filter3 = config['filter3']
    if config['ip']:
        ip = config['ip']
        pwd = config['pwd']
        ph = ParamikoHelper(ssh_username=user_name, remote_ip=ip, ssh_password=pwd)
    else:
        ph = ParamikoHelper(ssh_username=user_name)
    service_list_all = ['tax_service', 'pit_cal_api', 'cache_service', 'warning_api2', 'etl_service', 'financial_api']
    #################################################

    '''↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ 服务日志 ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓'''
    # out = ph.exec_shell('tail /home/%s/log/log_%s.txt -n %d' % (user_name, 'pit_cal_api', 100), is_print=0)
    out = ph.exec_shell(cmd, is_print=0)
    # out = ph.exec_shell('tail /home/%s/log/log_%s.txt -n %d' % (user_name, 'warning_api2', 100), is_print=0)
    # out = ph.exec_shell('tail /home/%s/log/log_%s.txt -n %d' % (user_name, 'etl_service', 100), is_print=0)

    if filter:
        for o in out:
            if filter in o:
                if filter2 in o:
                    if filter3 in o:
                        print(o)
    else:
        for o in out:
            print(o)


if __name__ == '__main__':
    config = {
        'user_name': 'rubinstein',  # rubinstein pit_v2 pit_prd aitai zgc demo
        'service_name': 'financial_api',  # ['tax_service', 'pit_cal_api', 'cache_service', 'warning_api2', 'etl_service', 'financial_api']
        'filter': "",
        'filter2': '',
        'filter3': '',
        'ip': '',  # 172.16.9.63
        'pwd': ''  # 1qazXSW@
        # 'ip': '172.16.9.63',  # 172.16.9.63
        # 'pwd': '1qazXSW@'  # 1qazXSW@
    }
    cmd = 'tail /home/%s/log/log_%s.txt -n %d' % (config['user_name'], config['service_name'], 200)
    main(config, cmd)










