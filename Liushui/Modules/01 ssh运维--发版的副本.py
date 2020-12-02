import paramiko
import time
import os
import util.my_functions as fun


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


def kill_one_service(ph, user_name, service):
    time.sleep(0.1)

    # kill 进程
    pid = ph.get_pid(service, user_name)
    if not pid:
        print('%s %s is not running' % (service, ((30 - len(service)) * '.')))

    else:
        ph.exec_shell('kill ' + pid)
        print('%s %s stop' % (service, ((30 - len(service)) * '.')))


def start_one_service(ph, service):
    time.sleep(0.2)

    # 启动服务
    try:
        ph.exec_shell('nohup python3 -u %s.py >> log/log_%s.txt &' % (service, service))
        print('%s %s run' % (service, ((30 - len(service)) * '.')))

    except:
        pass


def main(user_name, service_list, ip, pwd, env_config):
    if ip:
        ph = ParamikoHelper(ssh_username=user_name, remote_ip=ip, ssh_password=pwd)
    else:
        ph = ParamikoHelper(ssh_username=user_name)

    service_list_all = ['tax_service', 'pit_cal_api', 'cache_service', 'warning_api2', 'etl_service', 'financial_api']

    print('env: %s' % user_name)
    print('service_list: %s' % str(service_list))
    print('')
    time.sleep(0.1)

    '''↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓'''

    files = fun.get_all_filename('/Users/mass/SynologyDrive/PycharmProject/pit/user_data')
    new_files = []
    for x in files:
        if '.pyc' in x:
            continue
        if '__init__' in x:
            continue
        new_files.append(x)

    for file in new_files:
        file_name = file.split('/')[-1]
        ph.sftp_put_file(file, '/home/%s/user_data/%s' % (user_name, file_name))
        print('upload file: %s' % file_name)

    ph.sftp_put_file('/Users/mass/SynologyDrive/PycharmProject/pit/util/my_functions.py', '/home/%s/util/my_functions.py' % (user_name))
    print('upload file: %s.py' % 'my_functions')
    ph.sftp_put_file('/Users/mass/SynologyDrive/PycharmProject/pit/util/api_doc.py', '/home/%s/util/api_doc.py' % (user_name))
    print('upload file: %s.py' % 'api_doc')

    for service in service_list:  # service = 'warning_api2'
        ph.sftp_put_file('%s/%s/%s.py' % (os.getcwd().replace('/运维测试', ''), env_config[user_name]['env_path'], service), '/home/%s/%s.py' % (user_name, service))
        print('%s %s uploaded' % (service, ((30 - len(service)) * '.')))

    print('')
    for service in service_list:  # service = 'warning_api2'
        kill_one_service(ph, user_name, service)
        time.sleep(0.1)

    print('')
    for service in service_list:  # service = 'warning_api2'
        start_one_service(ph, service)
        time.sleep(0.1)

    '''↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓'''

    # 单独查看shell命令
    print('')
    time.sleep(0.2)
    config = {
        'tag': 'python3 -u'
    }

    out = ph.exec_shell('ps -ef --sort=ruid| grep python', is_print=0)

    for x in out.copy():
        if ('grep ' in x) | (x[:4] == 'root'):
            out.remove(x)
            continue
        if user_name[:7] in x:
            print(x)
        else:
            out.remove(x)

    service_num = 0
    for x in out:
        if (config['tag'] in x) & (user_name[:7] in x):
            service_num += 1

    non_start = []
    for x in service_list_all:
        if x in str(out):
            continue
        else:
            non_start.append(x)

    print('service filter: %s  total: %d  non_started: %s' % (config['tag'], service_num, str(non_start)))


if __name__ == '__main__':
    # 配置区
    #################################################
    user_name = 'rubinstein'  # rubinstein pit_v2 pit_prd aitai demo zgc
    service_list = ['financial_api']  # pdf_service
    # ['tax_service', 'pit_cal_api', 'cache_service', 'warning_api2', 'etl_service', 'financial_api']
    ip = ''  # 172.16.9.63
    pwd = ''  # 1qazXSW@
    # ip = '172.16.9.63'  # 172.16.9.63
    # pwd = '1qazXSW@'  # 1qazXSW@
    env_config = {
        'rubinstein': {'env_path': ''},
        'aitai': {'env_path': ''},
        'demo': {'env_path': 'env/demo'},
        'zgc': {'env_path': 'env/zgc'},
        'pit_v2': {'env_path': 'env/pit_v2'},
        'pit_prd': {'env_path': 'env/pit_prd'}
    }
    #################################################
    main(user_name, service_list, ip, pwd, env_config)
    print('Done %s'%fun.timestamp())





