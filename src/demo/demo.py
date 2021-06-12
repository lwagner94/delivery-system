from PyQt5 import QtWidgets, uic
import resources
import sys

AUTH_HOST = "localhost"
AUTH_PORT = "5000"

GEO_HOST = "localhost"
GEO_PORT = "80"

customer_token = None
agent_token = None


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('demo.ui', self)

        self.lbl_cust_response  = self.findChild(QtWidgets.QLabel, 'lbl_cust_resp')

        self.btn_cust_log_inout = self.findChild(QtWidgets.QPushButton, 'btn_cust_login')
        self.le_cust_username   = self.findChild(QtWidgets.QLineEdit, 'le_cust_user')
        self.le_cust_passwd     = self.findChild(QtWidgets.QLineEdit, 'le_cust_passwd')
        self.btn_cust_log_inout.clicked.connect(self.cust_loginout_pressed)

        self.le_job_pickup      = self.findChild(QtWidgets.QLineEdit, 'le_pickup')
        self.le_job_deliver_at  = self.findChild(QtWidgets.QLineEdit, 'le_deliver_at')
        self.le_job_decription  = self.findChild(QtWidgets.QLineEdit, 'le_description')
        self.btn_post_job       = self.findChild(QtWidgets.QPushButton, 'btn_post_job')
        self.btn_post_job.clicked.connect(self.cust_post_job)

        self.btn_cust_refresh_jobs  = self.findChild(QtWidgets.QPushButton, 'btn_cust_refresh_jobs')
        self.btn_cust_details_jobs  = self.findChild(QtWidgets.QPushButton, 'btn_cust_details_jobs')
        self.lv_cust_jobs           = self.findChild(QtWidgets.QListView, 'lv_cust_jobs')
        self.btn_cust_refresh_jobs.clicked.connect(self.cust_update_job_list)
        self.btn_cust_details_jobs.clicked.connect(self.cust_detail_job_list)


        self.le_geo_addr            = self.findChild(QtWidgets.QLineEdit, 'le_addr_query')
        self.btn_geo_translate      = self.findChild(QtWidgets.QPushButton, 'btn_geo_translate')
        self.btn_geo_translate.clicked.connect(self.geo_translate)
        self.le_ag_long             = self.findChild(QtWidgets.QLineEdit, 'le_ag_long')
        self.le_ag_lat              = self.findChild(QtWidgets.QLineEdit, 'le_ag_lat')

        self.btn_ag_log_inout = self.findChild(QtWidgets.QPushButton, 'btn_ag_login')
        self.le_ag_username   = self.findChild(QtWidgets.QLineEdit, 'le_ag_user')
        self.le_ag_passwd     = self.findChild(QtWidgets.QLineEdit, 'le_ag_passwd')
        self.btn_ag_log_inout.clicked.connect(self.ag_loginout_pressed)

        self.le_radius              = self.findChild(QtWidgets.QLineEdit, 'le_ag_radius')
        self.btn_ag_query_jobs      = self.findChild(QtWidgets.QPushButton, 'btn_ag_query_jobs')
        self.lv_ag_jobs_list        = self.findChild(QtWidgets.QListView, 'lv_ag_jobs_list')

        self.btn_ag_update_pos      = self.findChild(QtWidgets.QPushButton, 'btn_ag_update_pos')
        self.btn_ag_take            = self.findChild(QtWidgets.QPushButton, 'btn_ag_take')
        self.btn_ag_fin_job         = self.findChild(QtWidgets.QPushButton, 'btn_ag_fin_job')
        self.btn_ag_update_pos.clicked.connect(self.ag_update_pos)
        self.btn_ag_take.clicked.connect(self.ag_take_job)
        self.btn_ag_fin_job.clicked.connect(self.ag_fin_job)


        self.lbl_active_job         = self.findChild(QtWidgets.QLabel, 'lbl_active_job')
        self.lbl_ag_resp            = self.findChild(QtWidgets.QLabel, 'lbl_ag_resp')
        
        self.show()

    def cust_loginout_pressed(self):
        #Todo
        pass

    def cust_post_job(self):
        # Todo 
        pass

    def cust_update_job_list(self):
        # Todo 
        pass

    def cust_detail_job_list(self):
        # Todo 
        pass
    
    def geo_translate(self):
        # Todo 
        pass
    
    def ag_loginout_pressed(self):
        # Todo
        pass

    def ag_update_pos(self):
        # Todo
        pass

    def ag_take_job(self):
        # Todo
        pass

    def ag_fin_job(self):
        # Todo
        pass
    

app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()