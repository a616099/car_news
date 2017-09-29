# -*- coding: utf-8 -*-
from ftplib import FTP

def ftpconnect(host, username, password):
    ftp = FTP()
    # ftp.set_debuglevel(2)
    ftp.connect(host, 21)
    ftp.login(username, password)
    return ftp

def uploadfile(ftp, remotepath, localpath):
    bufsize = 1024
    path = '/'.join(remotepath.split('/')[:-1])
    try:
        ftp.mkd(path)
    except:
        pass
    fp = open(localpath, 'rb')
    ftp.storbinary('STOR ' + remotepath, fp, bufsize)
    ftp.set_debuglevel(0)
    fp.close()

if __name__ == "__main__":
    ftp = ftpconnect("192.168.1.29", "dssnews", "dssnews2017")
    uploadfile(ftp, "news163_pic/tesetser/test.txt", r"D:\ways\news163_pic\test.txt")

    ftp.quit()