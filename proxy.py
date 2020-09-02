# from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementNotVisibleException
import time , random
from threading import Thread
from os import sys
import pprint
import os
from os.path import join, dirname
from dotenv import load_dotenv
from twilio.rest import Client
import smtplib
import logging
from logging.handlers import RotatingFileHandler
import datetime
import re

def my_logging(log, f_name, msg):
    log.propagate = True
    fileh = RotatingFileHandler('static/logs/' + f_name + '.log', mode='a', maxBytes=log_file_size*1024, backupCount=2, encoding='utf-8', delay=0)
    # ('logs/' + f_name + '.log', 'a')
    fileh.setFormatter(formatter)
    for hdlr in log.handlers[:]:  # remove all old handlers
        log.removeHandler(hdlr)
    log.addHandler(fileh)
    log.critical(msg)
    log.propagate = False


def find_elem(collection, bb, ee, xpath):
    print("find_elem")
    for i in range(5):
        try:
            if collection == True:
                elem = ee.find_elements_by_xpath(xpath)
                print(xpath + "  ::  " + str(elem[0].is_displayed()))
                return (elem, elem[0].is_displayed())
            else:
                elem = ee.find_element_by_xpath(xpath)
                print(xpath + "  ::  " + str(elem.is_displayed()))
                return (elem, elem.is_displayed())
            
        except Exception as err:
            print(str(err))
            f_error_screen = True
        time.sleep(1)
    print("Not found Error: " + xpath)
    return (None, False)    


def send_email(log, msg, se_name, se_email, se_phone):
    sended = False    
    print("msg = " + msg)
                                                        
    my_logging(log, se_name, "[msg] " + msg)    
    # #################### email ##############################
    try:
        smtpObj = smtplib.SMTP('smtp.gmail.com: 587')#('smtp-mail.outlook.com', 587)
    except Exception as e:
        print(str(e))
        print(e)
        my_logging(log, se_name, str(e))#'SMTP TSL connection failed.  trying SMTP SSL connection...\n' + e)
        try:
            smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        except Exception as e:
            print(str(e))
            print(e)
            my_logging(log, se_name, 'SMTP SSL connection failed.  S M T P   F A I L E D\n' + str(e))
            return False
                                            
    try:
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.login(from_email, email_pass)
        smtpObj.sendmail(from_email, se_email, "Subject: Notification\n" + msg)
        smtpObj.quit()
        my_logging(log, se_name, 'email::  to:' + se_email + ' msg: ' + msg)
        sended = True
    except Exception as e:
        print(str(e))
        print(e)
        my_logging(log, se_name, 'SMTP Login failed.\n' + str(e))
                                                    

    # # ################### CALL ################################
    print(twilio_phone_number)
    print("---------------------------------------------")
    print("from_=" + twilio_phone_number + ", " + " to=" + se_phone + ", " + "body=" + msg)

    try:
        response_call = client.calls.create(twiml='<Response><Say>' + msg + '</Say></Response>', from_=twilio_phone_number, to=se_phone )
        if response_call.sid :                                                
            my_logging(log, se_name, 'CALL::  to:' + se_phone + ' msg: ' + msg)
            sended = True
    except  Exception as e:
        print(str(e))
        print(e)
        my_logging(log, se_name, str(e))

    # # ################### SMS ################################
    print(twilio_phone_number)
    print("---------------------------------------------")
    print("from_=" + twilio_phone_number + ", " + " to=" + se_phone + ", " + "body=" + msg)

    try:
        response_msg = client.messages.create(body=msg, from_=twilio_phone_number, to=se_phone )
        if response_msg.sid :
            my_logging(log, se_name, 'SMS::  to:' + se_phone + ' msg: ' + msg)
            sended = True
    except  Exception as e:
        print(str(e))
        print(e)
        my_logging(log, se_name,str(e))

    return sended     
            


class MyThread(Thread):
 
    def __init__(self, name, user):
        Thread.__init__(self)
        self.name = name 
        self.user = user
        dates = self.user["dates"].split(",")
        for i in range(len(dates)):
            dd_elem = dates[i].split("-")
            dates[i] = dd_elem[2] + dd_elem[1] + dd_elem[0]
        dates.sort()
        self.user["dates"] = dates
        self.log = logging.getLogger("a")  # root logger
 
    def run(self):
        global proxies_list, proxy_index , cur_error  

        while proxy_status[self.name] == 1 or proxy_status[self.name] == 4:
            start_time = time.perf_counter()
            if os.environ.get('USE_PROXY') == "true":
                proxy = proxies_list[proxy_index]
                proxy_index += 1
                if proxy_index == len(proxies_list): proxy_index = 0
            # is_redirected = False  # if it is true, current page is testcenterselect.aspx.

            path = '.\\Lib\\chromedriver.exe'
            options = webdriver.ChromeOptions ( ) 
            options.add_argument('--log-level=0')
            options.add_argument('ignore-certificate-errors')
            my_logging(self.log, self.user["name"], "USE_PROXY = " + os.environ.get('USE_PROXY'))
            my_logging(self.log, self.user["name"], "FREE_PROXY = " + os.environ.get('FREE_PROXY'))
            
            if os.environ.get('USE_PROXY') == "true":
                options.add_argument('--proxy-server=%s' % proxy)
            

            
            browser = webdriver.Chrome (executable_path = path, options = options )
            browser.maximize_window()
            browser.get("https://students-residents.aamc.org/")
            
            action = ActionChains(browser)
            
            if os.environ.get('USE_PROXY') == "true":
                my_logging(self.log, self.user["name"], 'now using proxy - ' + proxies_list[proxy_index])

            try:
                # Sign in Button
                if proxy_status[self.name] == 0: 
                    browser.close()
                    my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                    return

                elem, f = find_elem(False, browser, browser, "/html/body/div[4]/nav/header/div/div/div[2]/div[2]/ul/li[7]/a[contains(text(), 'Sign In')]")
                if f == False :
                    # elem, f = find_elem(False, browser, browser, "//body/div[1]/div/div/header/div/div[1]/div/div/a")
                    if f == False : raise Exception("Not found element")
                else:
                    print("True")
                elem.click()

                if proxy_status[self.name] == 0: 
                    browser.close()
                    my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                    return
                    

                # Username 
                elem, f = find_elem(False, browser, browser, "//body/oneaamc-root/oneaamc-layout/div/oneaamc-login-route/oneaamc-login-container/div/div/div[1]/div/oneaamc-authentication-form/div/form/div/div[1]/oneaamc-callback-input/mat-form-field/div/div[1]/div[3]/input")
                while not f:
                    elem, f = find_elem(False, browser, browser, "//body/oneaamc-root/oneaamc-layout/div/oneaamc-login-route/oneaamc-login-container/div/div/div[1]/div/oneaamc-authentication-form/div/form/div/div[1]/oneaamc-callback-input/mat-form-field/div/div[1]/div[3]/input")
                time.sleep(5)
                print("1")
                while True:
                    try:
                        elem.clear()
                        elem.send_keys(self.user["user_id"])
                        print("2")
                        break
                    except :
                        print("3")
                        elem, f = find_elem(False, browser, browser, "//body/oneaamc-root/oneaamc-layout/div/oneaamc-login-route/oneaamc-login-container/div/div/div[1]/div/oneaamc-authentication-form/div/form/div/div[1]/oneaamc-callback-input/mat-form-field/div/div[1]/div[3]/input")
                    time.sleep(1)

                # Password
                elem, f = find_elem(False, browser, browser, "//body/oneaamc-root/oneaamc-layout/div/oneaamc-login-route/oneaamc-login-container/div/div/div[1]/div/oneaamc-authentication-form/div/form/div/div[2]/oneaamc-callback-input/mat-form-field/div/div[1]/div[3]/input")
                if f == False : raise Exception("Not found element")
                elem.send_keys(self.user["password"])
                time.sleep(2)
                
                # Sign in Button
                elem, f = find_elem(False, browser, browser, "//body/oneaamc-root/oneaamc-layout/div/oneaamc-login-route/oneaamc-login-container/div/div/div[1]/div/oneaamc-authentication-form/div/form/div/div[3]/button")
                if f == False : raise Exception("Not found element")
                elem.click() 

                if proxy_status[self.name] == 0: 
                    browser.close()
                    my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                    return
                    
                time.sleep(10)    

                if proxy_status[self.name] == 0: 
                    browser.close()
                    my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                    return
                         

                # Feedback - No, thanks Button
                elem, f = find_elem(False, browser, browser, "//body/div[12]/div/div/section[3]/button[2]")                
                if f : elem.click()
                print("After Feedback")

                if proxy_status[self.name] == 0: 
                    browser.close()
                    my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                    return
                
                # Applying to Medical School
                elem, f = find_elem(False, browser, browser, "//body/div[4]/header/div/div[1]/div[1]/div/div/div[2]/div/p[contains(text(),'Applying to Medical School')]")
                if f == False : raise Exception("Not found element")
                print("Begin Action 1")
                action = ActionChains(browser)
                action.move_to_element(elem).perform()
                print("After Action 1")
                print("ok 1")
                time.sleep(1)

                if proxy_status[self.name] == 0: 
                    browser.close()
                    my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                    return

                # Register for the MCAT Exam
                elem, f = find_elem(False, browser, browser, "//div[1]/div[2]/div[2]/div/div/div[2]/ul/li[4]/a[contains(text(),'Register for the MCAT Exam')]")
                if f == False : raise Exception("Not found element")
                print("ok 2" + str(elem.is_displayed()))

                
                browser.get(elem.get_attribute("href"))

                if proxy_status[self.name] == 0: 
                    browser.close()
                    my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                    return
                    
                time.sleep(10)

                if proxy_status[self.name] == 0: 
                    browser.close()
                    my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                    return
                    

                # Feedback - No, thanks Button
                elem, f = find_elem(False, browser, browser, "//body/div[13]/div/div/section[3]/button[2]")                
                if f : elem.click()
                print("After Feedback")

                if proxy_status[self.name] == 0: 
                    browser.close()
                    my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                    return                    

                elem, f = find_elem(False, browser, browser, "/html/body/div[6]/div[3]/div[2]/div/div/div[2]/div/div[2]/div/div/div[1]/span/a")
                if f == False : raise Exception("Not found element")
                elem.click()

                if proxy_status[self.name] == 0: 
                    browser.close()
                    my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                    return
                    

                original_window = browser.current_window_handle

                for window_handle in browser.window_handles:
                    if window_handle != original_window:
                        browser.switch_to.window(window_handle)
                    else:
                        browser.close()


                if proxy_status[self.name] == 0: 
                    browser.close()
                    my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                    return
                    

                elem, f = find_elem(False, browser, browser, "//div[@id='loading-spinner']")
                if not f:
                    while not f:                        
                        elem, f = find_elem(False, browser, browser, "//div[@id='loading-spinner']")
                        print("f1 = " + str(f))
                        time.sleep(1)
                
                if proxy_status[self.name] == 0: 
                    browser.close()
                    my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                    return
                    
                
                while f:
                    print("f2 = " + str(f))
                    elem, f = find_elem(False, browser, browser, "//div[@id='loading-spinner']")
                    time.sleep(1)

                if proxy_status[self.name] == 0: 
                    browser.close()
                    my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                    return
                    
                

                

                elem, f = find_elem(False, browser, browser, "/html/body/mcat-root/div/div/ui-view/home/div/ui-view/dashboard/div/div[1]/div[2]/div[4]/a")
                if f == False : raise Exception("Not found element")
                elem.click()

                if proxy_status[self.name] == 0: 
                    browser.close()
                    my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                    return
                    
                time.sleep(5)

                if proxy_status[self.name] == 0: 
                    browser.close()
                    my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                    return
                    

                elem, f = find_elem(False, browser, browser, "/html/body/div[5]/div/div[3]/div[1]/div[3]/form[2]/div/div[2]/a")
                if f == False : raise Exception("Not found element")
                elem.click()

                if proxy_status[self.name] == 0: 
                    browser.close()
                    my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                    return
                    
                time.sleep(5)

                if proxy_status[self.name] == 0: 
                    browser.close()
                    my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                    return
                    

                # Reschedule
                elem, f = find_elem(False, browser, browser, "/html/body/div[5]/div/div[3]/div[1]/div[3]/form/table/tbody/tr[2]/td[4]/input[1]")
                if f == False : raise Exception("Not found element")
                elem.click()

                if proxy_status[self.name] == 0: 
                    browser.close()
                    my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                    return
                    
                time.sleep(2)

                if proxy_status[self.name] == 0: 
                    browser.close()
                    my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                    return
                    

                while (proxy_status[self.name] == 1 or proxy_status[self.name] == 4) and time.perf_counter() - start_time < proxy_period * 60:
                    # Open Calendar
                    elem, f = find_elem(False, browser, browser, "/html/body/div[5]/div/div[3]/div[1]/div[4]/form/div/fieldset/div[1]/div/div/div[2]/div[2]/div/div/div/div/img")
                    if f == False : raise Exception("Not found element")
                    elem.click()

                    if proxy_status[self.name] == 0: 
                        browser.close()
                        my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                        return
                        
                    time.sleep(5)

                    if proxy_status[self.name] == 0: 
                        browser.close()
                        my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                        return
                        

                    elems, f = find_elem(True, browser, browser, "//table[contains(@class, 'calendar')]//td[@data-handler='selectDay']/a")
                    if f == False : raise Exception("Not found element")

                    if proxy_status[self.name] == 0: 
                        browser.close()
                        my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                        return
                        

                    for elem_index in range(len(elems)):
                        # Open Calendar
                        elem_, f = find_elem(False, browser, browser, "/html/body/div[5]/div/div[3]/div[1]/div[4]/form/div/fieldset/div[1]/div/div/div[2]/div[2]/div/div/div/div/img")
                        if f == False : raise Exception("Not found element")
                        elem_.location_once_scrolled_into_view
                        time.sleep(2)
                        print("calendar clicked.")
                        elem_.click()

                        if proxy_status[self.name] == 0: 
                            browser.close()
                            my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                            return
                            
                        time.sleep(5)

                        if proxy_status[self.name] == 0: 
                            browser.close()
                            my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                            return
                            

                        elems, f = find_elem(True, browser, browser, "//table[contains(@class, 'calendar')]//td[@data-handler='selectDay']/a")
                        if f == False : raise Exception("Not found element")

                        if proxy_status[self.name] == 0: 
                            browser.close()
                            my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                            return

                        elem = elems[elem_index]


                        print("elem ::::::::::::::::::::::::::::::::::::::::")
                        
                        print("After sleep")
                        ddd_1 = " ".join(re.split(" +", elem.get_attribute("aria-label"))[:3])
                        print("ddd_1 = " + ddd_1)
                        for dd in self.user["dates"]:
                            print(dd)
                            ddd_2 = datetime.datetime(int(dd[:4]), int(dd[4:6]), int(dd[-2:])).strftime('%B %d %Y').split(" ")
                            ddd_2[1] = str(int(ddd_2[1]))
                            ddd_2 = " ".join(ddd_2)
                            print("ddd_2 = " + ddd_2)
                            if ddd_1 == ddd_2:
                                print("::::::::::::::::::::::::::::::::::::::OK")
                                elem.click()

                                if proxy_status[self.name] == 0: 
                                    browser.close()
                                    my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                                    return
                                    

                                for key, location_list in self.user["locations"].items():
                                    print("ok")
                                    print("len = " + str(len(location_list)))
                                    for location in location_list:
                                        print("location = " + location["s"])
                                        # print("location : " + location["l"] + " , center_number : " + location["c"])
                                        # Search Text                            
                                        elem, f = find_elem(False, browser, browser, "//body/div[5]/div/div[3]/div[1]/div[4]/form/div/fieldset/div[1]/div/div/div[2]/div[1]/div/input")
                                        if f == False : raise Exception("Not found Search TextBox ")
                                        elem.location_once_scrolled_into_view
                                        time.sleep(2)
                                        elem.clear()
                                        elem.send_keys(location["s"])
                                        
                                        ######## break ##############
                                        if proxy_status[self.name] == 0: 
                                            browser.close()
                                            my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                                            return
                                        # Search Button            
                                        elem, f = find_elem(False, browser, browser, "//body/div[5]/div/div[3]/div[1]/div[4]/form/div/fieldset/div[1]/div/div/div[2]/div[3]/span/input[2]")
                                        if f == False : raise Exception("Not found Search Button")
                                        elem.click()

                                        if proxy_status[self.name] == 0: 
                                            browser.close()
                                            my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                                            return
                                            
                                        time.sleep(5)

                                        if proxy_status[self.name] == 0: 
                                            browser.close()
                                            my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                                            return
                                            

                                        # Search Time
                                
                                        
                                        # if f == False : 
                                        #     # Multi
                                        #     elems, f = find_elem(True, browser, browser, "//body/div[5]/div/div[3]/div[1]/div[4]/form/div/fieldset/div[3]/div/div[1]/div/span/table/tbody/tr//td[3]/span[3]/input")

                                        send_ok = False
                                        while (proxy_status[self.name] == 1 or proxy_status[self.name] == 4) and time.perf_counter() - start_time < proxy_period * 60:
                                            elems, f = find_elem(True, browser, browser, "//body/div[5]/div/div[3]/div[1]/div[4]/form/div/fieldset/div[3]/div/div[1]/div/span/table/tbody/tr/td[3]/span[3]/input")
                                            if proxy_status[self.name] == 0: 
                                                browser.close()
                                                my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                                                return
                                                
                                            if f:
                                                for elem in elems:
                                                    ######## break ##############
                                                    if proxy_status[self.name] == 0: 
                                                        browser.close()
                                                        my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                                                        return
                                                    while True:
                                                        try:
                                                            elem.location_once_scrolled_into_view
                                                            break
                                                        except:
                                                            time.sleep(1)
                                                    ######## break ##############
                                                    if proxy_status[self.name] == 0: 
                                                        browser.close()
                                                        my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                                                        return
                                                    tr = elem.find_element_by_xpath("./ancestor::tr")
                                                    tc_name = tr.find_element_by_xpath("./td[2]/div[1]").text
                                                    tc_address = ", ".join(tr.find_element_by_xpath("./td[2]/div[2]").text.splitlines()[:-1])
                                                    mile = tr.find_element_by_xpath("./td[4]").text
                                                    mile = float(re.split(" +", mile)[0])
                                                    print("tc_name: " + tc_name)
                                                    print("tc_address: " + tc_address)
                                                    print("mile: " + str(mile))
                                                    tt = elem.get_attribute("value")
                                                    if tt.find("Select") > -1:                                                
                                                        elem.click()

                                                        if proxy_status[self.name] == 0: 
                                                            browser.close()
                                                            my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                                                            return
                                                        
                                                        time.sleep(1)
                                                        tts = elem.find_elements_by_xpath("./ancestor::tr/td[3]/span[3]/div/table/tbody/tr/td/input")
                                                        for ttt in tts:
                                                            ######## break ##############
                                                            if proxy_status[self.name] == 0: 
                                                                browser.close()
                                                                my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                                                                return
                                                            tttt = ttt.get_attribute("value")
                                                            print("time: " + str(tttt) + "  " + ("0" + location["t"])[-5:] )
                                                            if location["t"] == "" or (("0" + location["t"])[-5:] == str(tttt)) :
                                                                print("time OK")
                                                                if location["m"] == "" or (float(location["m"]) >= mile):                                                            

                                                                    msg = os.environ.get("MESSAGE").replace("%NAME", self.user["name"]).replace("%DATE", ddd_1).replace("%LOCATION", tc_address).replace("%TIME", location["t"])
                                                                    if send_email(self.log, msg, self.user["name"], self.user["email"], self.user["phone"]): 
                                                                        send_ok = True   

                                                                        ttt.click()
                                                                        time.sleep(5)                                                             

                                                                        elem, f = find_elem(False, browser, browser, "//body/div[5]/div/div[3]/div[1]/div[4]/form/div/div/div[3]/div/div/input[2]")
                                                                        if f == False : raise Exception("Not found Button")
                                                                        elem.click()
                                                                        time.sleep(2)

                                                                        if agree == "true":
                                                                            elem, f = find_elem(False, browser, browser, "//body/div[10]/div[2]/div[2]/div/div/input[2]")
                                                                        else:
                                                                            elem, f = find_elem(False, browser, browser, "//body/div[10]/div[2]/div[2]/div/div/input[1]")
                                                                        if f == False : raise Exception("Not found Button")
                                                                        elem.location_once_scrolled_into_view
                                                                        elem.click()
                                                                        time.sleep(2)
                                                                        proxy_status[self.name] = 2
                                                                        my_logging(self.log, self.user["name"], " Message sent.") 
                                                                        browser.close()
                                                                        return
                                                                    
                                                                        

                                                                    
                                                                    
                                                                    
                                                        
                                                    else:
                                                        print("time: " + str(tt))
                                                        if location["t"] != "" and (("0" + location["t"])[-5:] != str(tt)): continue
                                                        print("OK")
                                                        if location["m"] == "" or (float(location["m"]) >= mile):                                                        

                                                            msg = os.environ.get("MESSAGE").replace("%NAME", self.user["name"]).replace("%DATE", ddd_1).replace("%LOCATION", tc_address).replace("%TIME", location["t"])
                                                            if send_email(self.log, msg, self.name, self.user["email"], self.user["phone"]): 
                                                                send_ok = True                                   

                                                                elem.click()
                                                                time.sleep(5)                             

                                                                elem, f = find_elem(False, browser, browser, "//body/div[5]/div/div[3]/div[1]/div[4]/form/div/div/div[3]/div/div/input[2]")
                                                                if f == False : raise Exception("Not found Button")
                                                                elem.click()
                                                                time.sleep(2)

                                                                if agree == "true":
                                                                    elem, f = find_elem(False, browser, browser, "//body/div[10]/div[2]/div[2]/div/div/input[2]")
                                                                else:
                                                                    elem, f = find_elem(False, browser, browser, "//body/div[10]/div[2]/div[2]/div/div/input[1]")
                                                                if f == False : raise Exception("Not found Button")
                                                                elem.location_once_scrolled_into_view
                                                                elem.click()
                                                                time.sleep(2)
                                                                proxy_status[self.name] = 2
                                                                my_logging(self.log, self.user["name"], " appointment found.") 
                                                                browser.close()
                                                                return

                                            print("Before last_mile")

                                            last_mile, f = find_elem(False, browser, browser, "//body/div[5]/div/div[3]/div[1]/div[4]/form/div/fieldset/div[3]/div/div[1]/div/span/table/tbody/tr[not(contains(@style, 'display: none;'))][last()]/td[4]")
                                            print("After last_mile")
                                            if f == False : break
                                            print("1")
                                            
                                            if proxy_status[self.name] == 0: 
                                                browser.close()
                                                my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                                                return
                                            print("2")
                                            
                                            last_mile = float(re.split(" +", last_mile.text)[0])
                                            print("3")
                                            print("##" + location["m"] + "##  " + str(last_mile))
                                            if location["m"] != "" and (float(location["m"]) < last_mile):
                                                print("4")
                                                my_logging(self.log, self.user["name"], str(last_mile) + " > " + location["m"])
                                                print("5")
                                                break     

                                            print("Before show_more")                                       
                                            show_more, f = find_elem(False, browser, browser, "//body/div[5]/div/div[3]/div[1]/div[4]/form/div/fieldset/div[3]/div/div[1]/div/p[1]/a")
                                            print("After show_more")
                                            if f == False : break

                                            if proxy_status[self.name] == 0: 
                                                browser.close()
                                                my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                                                return
                                            print("Before show_more.location_once_scrolled_into_view")
                                            show_more.location_once_scrolled_into_view
                                            print("After show_more.location_once_scrolled_into_view")
                                            show_more.click()

                                            overlay, f = find_elem(False, browser, browser, "//*[@class='ui-widget-overlay ui-front']")
                                            if f == False : 
                                                while not f:
                                                    overlay, f = find_elem(False, browser, browser, "//*[@class='ui-widget-overlay ui-front']")
                                                    time.sleep(1)

                                            if proxy_status[self.name] == 0: 
                                                browser.close()
                                                my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                                                return
                                            
                                            print("overlay on")
                                            while f:
                                                overlay, f = find_elem(False, browser, browser, "//*[@class='ui-widget-overlay ui-front']")
                                                time.sleep(1)

                                            if proxy_status[self.name] == 0: 
                                                browser.close()
                                                my_logging(self.log, self.user["name"], proxies_list[proxy_index] + ': Browser is stopped by admin.')
                                                return
                                            
                                            print("overlay off")
                                            # browser.find_element_by_tag_name('body').send_keys(Keys.HOME)
                                            time.sleep(2)
                                            # if location["c"] != "":
                                            #     if tc_address.find(location["c"]) < 0 :continue
                                        print("breaked")
                    print("Before Refresh")
                    browser.refresh()
                    print("After Refresh")
                    time.sleep(5)
              

            except Exception as e: 
                print(" Exception : " + e.args[0])
                my_logging(self.log, self.user["name"], " Exception : " + e.args[0])                    
                if e.args[0] == "date_missed":                    
                    proxy_status[self.name] = 4
                    my_logging(self.log, self.user["name"], " Date Missed.")
                if e.args[0] == "defer_cancel":
                    proxy_change = False
                    
                cur_error = e.args[0] 
                browser.close() 

                time.sleep(sleep_period)   

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Get Twilio Account Info
account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
twilio_phone_number = os.environ.get('TWILIO_PHONE_NUMBER')
client = Client(account_sid, auth_token)

from_email = os.environ.get('EMAIL_ADDRESS')
email_pass = os.environ.get('EMAIL_PASSWORD')
if os.environ.get('FAST_MODE') == "true":
    fast_mode = True
else:
    fast_mode = False

log_file_size = float(os.environ.get('LOG_FILE_SIZE'))
proxy_period = float(os.environ.get('PROXY_PERIOD'))
sleep_period = float(os.environ.get('SLEEP_PERIOD'))
agree = os.environ.get('AGREE')

proxies_list = []
proxy_index = 0
proxy_status = {}

formatter = logging.Formatter('%(asctime)s    %(message)s')
cur_error = ""