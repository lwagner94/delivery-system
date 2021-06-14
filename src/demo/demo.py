from PyQt5 import QtWidgets, uic
import resources
import requests
import sys

SERVICE = "http://localhost:8000"

customer_token = None
agent_token = None

###############################################################################
# This demo is used to provide a simple UI to demonstrate the basic use cases #
# and debug the basic functionality of the developed service. Thus, the code  #
# includes a lot of copy/pasted code and does not include any checks!         #
#                                                                             #
# DO _NOT_ USE THIS CODE FOR ANYTHING ELSE THAN THE DEMO!                     #
#                                                                             #
###############################################################################


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('demo.ui', self)

        self.customer_token = None
        self.customer_selection = None

        self.agent_token = None
        self.agent_selection = None
        self.agent_job = None

        self.lbl_token_customer = self.findChild(QtWidgets.QLabel, 'lbl_token_customer')
        self.lbl_token_agent    = self.findChild(QtWidgets.QLabel, 'lbl_token_agent')

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
        self.lw_cust_jobs           = self.findChild(QtWidgets.QListView, 'lw_cust_jobs')
        self.te_cust_details        = self.findChild(QtWidgets.QTextEdit, 'te_job_details')
        self.btn_cust_refresh_jobs.clicked.connect(self.cust_update_job_list)
        self.btn_cust_details_jobs.clicked.connect(self.cust_detail_job_list)
        self.lw_cust_jobs.itemClicked.connect(self.customer_item_selected)


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
        self.lw_ag_jobs_list        = self.findChild(QtWidgets.QListView, 'lw_ag_jobs_list')
        self.lw_ag_jobs_list.itemClicked.connect(self.agent_item_selected)

        self.btn_ag_update_pos      = self.findChild(QtWidgets.QPushButton, 'btn_ag_update_pos')
        self.btn_ag_take            = self.findChild(QtWidgets.QPushButton, 'btn_ag_take')
        self.btn_ag_query           = self.findChild(QtWidgets.QPushButton, 'btn_ag_query_jobs')
        self.btn_ag_fin_job         = self.findChild(QtWidgets.QPushButton, 'btn_ag_fin_job')
        self.btn_ag_update_pos.clicked.connect(self.ag_update_pos)
        self.btn_ag_take.clicked.connect(self.ag_take_job)
        self.btn_ag_query.clicked.connect(self.ag_query)
        self.btn_ag_fin_job.clicked.connect(self.ag_fin)


        self.lbl_active_job         = self.findChild(QtWidgets.QLabel, 'lbl_active_job')
        self.lbl_ag_resp            = self.findChild(QtWidgets.QLabel, 'lbl_ag_resp')
        
        self.show()

    def cust_loginout_pressed(self):
        try:
            if self.customer_token is None:
                res = requests.post(SERVICE + "/auth/login", 
                                    json={"email": self.le_cust_user.text(), 
                                        "password": self.le_cust_passwd.text()})
                
                if res.status_code == 200:
                    self.customer_token = res.json()['token']
                    self.lbl_token_customer.setText(self.customer_token)
                    self.btn_cust_log_inout.setText("Logout")
                    self.lbl_cust_response.setText("OK. Logged in.")
                    return

                self.lbl_cust_response.setText("Error status code! Staus: {}".format(res.status_code))

            else:
                headers = { "Authorization": "Bearer {0}".format(self.customer_token)}
                res = requests.get(SERVICE + "/auth/user/self", headers=headers)

                if res.status_code == 200:
                    self.customer_token = None
                    self.lbl_token_customer.setText("None.")
                    self.btn_cust_log_inout.setText("Login")
                    self.lbl_cust_response.setText("OK. Logged out.")
                    return

        except Exception as ex:
            self.lbl_cust_response.setText("Error! See log.")
            print(ex)


    def cust_post_job(self):
        if self.customer_token is None:
            self.lbl_cust_response.setText("Not logged in!")
            return

        try:
            headers = { "Authorization": "Bearer {0}".format(self.customer_token)}
            res = requests.post(SERVICE + "/job", 
                                json={"pickup_at": self.le_job_pickup.text(), 
                                    "deliver_at": self.le_job_deliver_at.text(),
                                    "description": self.le_job_decription.text()},
                                headers=headers)
            
            if res.status_code == 201:
                self.lbl_cust_response.setText("Created!")
                return

            self.lbl_cust_response.setText("Error! Status code: {}".format(res.status_code))

        except Exception as ex:
            self.lbl_cust_response.setText("Error! See log.")
            print(ex)


    def cust_update_job_list(self):
        if self.customer_token is None:
            self.lbl_cust_response.setText("Not logged in!")
            return

        try:
            headers = { "Authorization": "Bearer {0}".format(self.customer_token)}
            params = {"provider_user_id": "self"}
            res = requests.get(SERVICE + "/job", params=params, headers=headers)
            
            if res.status_code == 200:
                jobs = []
                for j in res.json():
                    jobs.append("{} -> {} {} {}".format(j['pickup_at'], j['deliver_at'], j['description'], j['job_id']))

                self.lw_cust_jobs.clear()
                self.lw_cust_jobs.addItems(jobs)
                self.lbl_cust_response.setText("List Created!")
                return

            self.lbl_cust_response.setText("Error! Status code: {}".format(res.status_code))

        except Exception as ex:
            self.lbl_cust_response.setText("Error! See log.")
            print(ex)


    def cust_detail_job_list(self):
        if self.customer_selection is None:
            self.lbl_cust_response.setText("No selection!")
            return
            
        first, *middle, job_id = self.customer_selection.split()

        if self.customer_token is None:
            self.lbl_cust_response.setText("Not logged in!")
            return

        try:
            headers = { "Authorization": "Bearer {0}".format(self.customer_token)}
            res = requests.get(SERVICE + "/job/{}".format(job_id), headers=headers)
            
            if res.status_code == 200:
                self.te_cust_details.setPlainText(str(res.json()))
                self.lbl_cust_response.setText("Details printed!")
                return

            self.lbl_cust_response.setText("Error! Status code: {}".format(res.status_code))

        except Exception as ex:
            self.lbl_cust_response.setText("Error! See log.")
            print(ex)

    
    def geo_translate(self):
        if self.agent_token is None:
            self.lbl_ag_resp.setText("Agent not logged in!")
            return

        try:
            headers = { "Authorization": "Bearer {0}".format(self.agent_token)}
            params = {"address": "{}".format(self.le_geo_addr.text())}

            print(params)

            res = requests.get(SERVICE + "/geo/coordinates", params=params, headers=headers)

            if res.status_code == 200:
                self.le_ag_lat.setText(str(res.json()['latitude']))
                self.le_ag_long.setText(str(res.json()['longitude']))
                self.lbl_ag_resp.setText("Done.")
                return

            self.lbl_ag_resp.setText("Error! Wrong status code: {}".format(res.status_code))

        except Exception as ex:
            self.lbl_ag_resp.setText("Error! See log.")
            print(ex)
            
    
    def ag_loginout_pressed(self):
        try:
            if self.agent_token is None:
                res = requests.post(SERVICE + "/auth/login", 
                                    json={"email": self.le_ag_username.text(), 
                                        "password": self.le_ag_passwd.text()})
                
                if res.status_code == 200:
                    self.agent_token = res.json()['token']
                    self.lbl_token_agent.setText(self.agent_token)
                    self.btn_ag_log_inout.setText("Logout")
                    self.lbl_ag_resp.setText("OK. Logged in.")
                    return

                self.lbl_ag_resp.setText("Error status code! Staus: {}".format(res.status_code))

            else:
                headers = { "Authorization": "Bearer {0}".format(self.agent_token)}
                res = requests.get(SERVICE + "/auth/user/self", headers=headers)

                if res.status_code == 200:
                    self.agent_token = None
                    self.lbl_token_agent.setText("None.")
                    self.btn_ag_log_inout.setText("Login")
                    self.lbl_ag_resp.setText("OK. Logged out.")
                    return

        except Exception as ex:
            self.lbl_ag_resp.setText("Error! See log.")
            print(ex)


    def ag_update_pos(self):
        if self.agent_job is None:
            self.lbl_ag_resp.setText("No current job!")
            return

        try:
            headers = { "Authorization": "Bearer {0}".format(self.agent_token)}
            res = requests.put(SERVICE + "/agent/self", 
                                    json={"status": "idle",
                                        "longitude": float(self.le_ag_long.text()),
                                        "latitude": float(self.le_ag_lat.text()),
                                        "current_job": self.agent_job}, headers=headers)

            if res.status_code == 200:
                self.lbl_ag_resp.setText("Pushed update!")
                return

            self.lbl_ag_resp.setText("Error status code! Staus: {}".format(res.status_code))

        except Exception as ex:
            self.lbl_ag_resp.setText("Error! See log.")
            print(ex)


    def ag_take_job(self):
        if self.agent_selection is None:
            self.lbl_ag_resp.setText("No selection!")
            return


        if self.agent_job is not None:
            self.lbl_ag_resp.setText("Already a job taken!")
            return

        first, *middle, job_id = self.agent_selection.split()

        try:
            headers = { "Authorization": "Bearer {0}".format(self.agent_token)}
            res = requests.put(SERVICE + "/job/{}".format(job_id), 
                                    json={"status": "picked_up"}, headers=headers)

            if res.status_code == 200:
                self.lbl_ag_resp.setText("Job taken! :)")
                self.agent_job = job_id
                self.lbl_active_job.setText(job_id)
                self.lw_ag_jobs_list.clear()
                return

            self.lbl_ag_resp.setText("Error status code! Staus: {}".format(res.status_code))

        except Exception as ex:
            self.lbl_ag_resp.setText("Error! See log.")
            print(ex)


    def ag_query(self):
        if self.agent_token is None:
            self.lbl_ag_resp.setText("Not logged in!")
            return

        try:
            headers = { "Authorization": "Bearer {0}".format(self.agent_token)}
            res = None

            if self.le_ag_lat.text() != "" and self.le_ag_long.text() != "" and self.le_radius.text() != "":
                params = {  "radius": float(self.le_radius.text()), 
                            "longitude": float(self.le_ag_long.text()),
                            "latitude": float(self.le_ag_lat.text()),
                            "status": "open"}
            else:
                params = { "status": "open"}

            res = requests.get(SERVICE + "/job", headers=headers, params=params)
            
            if res.status_code == 200:
                jobs = []
                for j in res.json():
                    jobs.append("{} -> {} {} {}".format(j['pickup_at'], j['deliver_at'], j['description'], j['job_id']))

                self.lw_ag_jobs_list.clear()
                self.lw_ag_jobs_list.addItems(jobs)
                self.lbl_ag_resp.setText("List Created!")
                return

            self.lbl_ag_resp.setText("Error! Status code: {}".format(res.status_code))

        except Exception as ex:
            self.lbl_ag_resp.setText("Error! See log.")
            print(ex)


    def ag_fin(self):
        if self.agent_job is None:
            self.lbl_ag_resp.setText("No job to finish!")
            return

        try:
            headers = { "Authorization": "Bearer {0}".format(self.agent_token)}
            res = requests.put(SERVICE + "/job/{}".format(self.agent_job), 
                                    json={"status": "delivered"}, headers=headers)

            if res.status_code == 200:
                self.lbl_ag_resp.setText("Job done! :D")
                self.agent_job = None
                self.lbl_active_job.setText("None")
                self.lw_ag_jobs_list.clear()
                return

            self.lbl_ag_resp.setText("Error status code! Staus: {}".format(res.status_code))

        except Exception as ex:
            self.lbl_ag_resp.setText("Error! See log.")
            print(ex)


    def customer_item_selected(self, item):
        self.customer_selection = item.text()


    def agent_item_selected(self, item):
        self.agent_selection = item.text()


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()