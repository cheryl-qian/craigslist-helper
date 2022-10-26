import sys
import time
import configparser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


opts = Options()
opts.add_argument("--window-size=1000,1000")


chromedriver = None

def countdown(seconds):
    # print '\n'
    for count in range(seconds, 0, -1):
        if(seconds > 3):
            print('    **** Sleeping for %d seconds...\r' % count),
            sys.stdout.flush()
        time.sleep(1)


def login(email_handle, password):
    global chromedriver
    print("\nLogging into Craigslist...")
    email_field = chromedriver.find_element(By.CSS_SELECTOR, "input[name='inputEmailHandle']")
    email_field.send_keys(email_handle)
    password_field = chromedriver.find_element(By.CSS_SELECTOR, "input[name='inputPassword']")
    password_field.send_keys(password)

    sign_in_submit = chromedriver.find_element(By.CSS_SELECTOR, "button[class='accountform-btn']")
    sign_in_submit.click()
    countdown(5)

    title_present = chromedriver.find_elements(By.CSS_SELECTOR, "p[class='postinglist_title']")

    if len(title_present):
        print("Login Successful!  Continuing...")
        countdown(3)
    else:  # element not found
        print("Login Unsuccessful!  Exiting...")
        countdown(3)
        chromedriver.quit()
        exit(1)


def logout():
    global chromedriver  # use the global chromedriver variable.
    logout_link = chromedriver.find_element(By.CSS_SELECTOR, "a[href*='logout']")
    logout_link.click()
    print("Successfully logged out of Craigslist.")


def open_new_tab(link):
    global chromedriver
    chromedriver.execute_script("window.open('');")
    chromedriver.switch_to.window(chromedriver.window_handles[1])
    chromedriver.get(link)
    countdown(5)


def check_for_renewals():
    global chromedriver
    renew_links = chromedriver.find_elements(By.XPATH, "//input[contains(@class, 'managebtn') and contains(@value, 'repost')]")
    return renew_links


def click_renew_links(renew_links):
    global chromedriver
    for link in renew_links:
        renew_URL = link.find_element(By.XPATH,"..").get_attribute('action')
        open_new_tab(renew_URL)
        renew_button = chromedriver.find_element(By.XPATH, "//input[contains(@class, 'managebtn') and contains(@value, 'Repost this Posting')]")
        renew_button.click()
        countdown(3)
        continue_button = chromedriver.find_element(By.XPATH,"//button[contains(@value, 'continue')]")
        continue_button.click()
        countdown(3)
        publish_button = chromedriver.find_element(By.XPATH,"//button[contains(@value, 'Continue')]")
        publish_button.click()
        countdown(5)
        renewed_text = chromedriver.find_elements(By.XPATH, "//*[contains(text(), 'Thanks for posting')]")
        if len(renewed_text):
            print("\n Listing reposted!")
        else:
            print("Listing possibly not reposted; something went wrong!")
        chromedriver.close()
        chromedriver.switch_to.window(chromedriver.window_handles[0])
        countdown(3)



# main method
def main():
    global chromedriver

    chromedriver = webdriver.Chrome(executable_path='./chromedriver', options=opts)
    chromedriver.get('https://accounts.craigslist.org/login/home')

    config = configparser.ConfigParser()
    config.read('relist.ini')
    email_handle = config.get('craigslist.org', 'EmailHandle')
    password = config.get('craigslist.org', 'Password')

    login(email_handle, password)

    renew_links = check_for_renewals()
    if len(renew_links):
        print(("%d listings eligible for repost have been found!") % len(renew_links))
        click_renew_links(renew_links)
    else:
        print("No listings to repost.  Exiting!")

    logout()

    print("\n Exiting script!")
    chromedriver.quit()
    exit(0)


if __name__ == '__main__':
    main()
