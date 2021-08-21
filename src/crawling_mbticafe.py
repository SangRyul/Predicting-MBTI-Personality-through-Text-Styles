#!/usr/bin/env python
# coding: utf-8

# ### 기본 세팅

# In[1]:


from os import error
import time
import pandas as pd
import pickle

from selenium import webdriver
import pyperclip
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys


# ### 네이버 카페 로그인

# In[2]:


# 로그인시 복붙하는 방법으로 캡챠 우회
def copy_input(xpath, input):
    pyperclip.copy(input)
    driver.find_element_by_xpath(xpath).click()
    ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
    time.sleep(1)


# In[3]:


driver = webdriver.Chrome('/home/sangryul/Desktop/chromedriver')
driver.implicitly_wait(3)


# In[4]:


# 네이버 로그인
naver_id = ''
naver_pw = ''

driver.get('https://nid.naver.com/nidlogin.login')             
time.sleep(1)

copy_input('//*[@id="id"]', naver_id)
copy_input('//*[@id="pw"]', naver_pw)

driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()


# ### 크롤링
# 한 페이지 테스트 while page <= 1:
# 모든 페이지 크롤링 while page > -1:

# In[5]:


def crawling_address_and_nickname(menuid):
    page = 400
    address = []
    nickname = []

    while page < 1000:
        #page += 1
        try:
            # 페이지 이동
            page += 1
            driver.get(f"https://cafe.naver.com/ArticleList.nhn?search.clubid=11856775&search.menuid={menuid}&search.boardtype=L&search.page={page}")
            try:
                driver.switch_to.frame("cafe_main")
            except:
                continue

            # 게시글 없을 경우
            try:
                if driver.find_element_by_class_name("nodata").text == '등록된 게시글이 없습니다.':
                    break
                    pass
            except:
                print("no article")
                #print(error)
                pass
  


            # 글 주소, 작성자 닉네임 크롤링
            for i in range(1, 16, 1):
                cur_address = driver.find_element_by_xpath(f"/html/body/div[1]/div/div[4]/table/tbody/tr[{i}]/td[1]/div[2]/div/a[1]").get_attribute("href")
                cur_nickname = driver.find_element_by_xpath(f"/html/body/div[1]/div/div[4]/table/tbody/tr[{i}]/td[2]/div/table/tbody/tr/td/a").get_attribute("onclick")
                address.append(cur_address)
                nickname.append(cur_nickname)

            driver.switch_to.default_content()   

        except:
            pass
        
    return address, nickname


# In[6]:


# nickname에 mbti가 있으면 추출
def find_mbti_in_nickname(nickname, mbti_group):
    for i in range(len(nickname)):
        nickname[i] = nickname[i].lower()
        
    drop_idx = []   
    for i in range(len(nickname)):
        check_cnt = 0

        for mbti in mbti_group:        
            if mbti in nickname[i]:
                nickname[i] = mbti

            if mbti not in nickname[i]:
                check_cnt += 1

        if check_cnt == 16:
            drop_idx.append(i)
            
    return nickname, drop_idx


# In[7]:


# nickname에 mbti가 없으면 드랍
def drop_idx_in_address_and_nickname(address, nickname, drop_idx):
    for i in range(len(address)):
        while i in drop_idx:
            address.pop(i)
            nickname.pop(i)
            drop_idx.remove(i)

            for idx in range(len(drop_idx)):
                drop_idx[idx] -= 1
                
    return address, nickname


# In[8]:


def crawling_title_and_content(address):
    title = []
    content = []
    
    for url in address:
        try:
            # 페이지 이동
            driver.get(url)
            driver.switch_to.frame("cafe_main")
            
            
            
            # 글 제목, 내용 크롤링
            cur_title = driver.find_element_by_css_selector("h3.title_text").text
            cur_content = driver.find_element_by_class_name("se-main-container").text
            title.append(cur_title)
            content.append(cur_content)

        except:
            pass
        
    return title, content


# In[9]:


def crawling(menuid, mbti_group):
    # 글 주소, 작성자 닉네임 크롤링
    print(' crawling address and nickname... ')
    start_time = time.time()
    address, nickname = crawling_address_and_nickname(menuid) 
    print('  progress time: {} seconds \n'.format(time.time() - start_time))
    
    
    
    print(' extracting mbti from nickname... ')
    start_time = time.time()
    nickname, drop_idx = find_mbti_in_nickname(nickname, mbti_group)                      # nickname에 mbti가 있으면 추출
    address, nickname = drop_idx_in_address_and_nickname(address, nickname, drop_idx)     # nickname에 mbti가 없으면 드랍
    print('  progress time: {} seconds \n'.format(time.time() - start_time))
    
    
    
    # 글 제목, 내용 크롤링
    print(' crawling title and content... ')
    start_time = time.time()
    title, content = crawling_title_and_content(address)
    print('  progress time: {} seconds \n'.format(time.time() - start_time))
    
    print(len(nickname), len(title), len(content))
    
    
    #data = pd.DataFrame({'mbti': nickname, 'title': title, 'content': content})
    json_data = {'mbti': nickname, 'title': title, 'content': content}
    data = pd.DataFrame.from_dict(json_data, orient='index')
    data = data.transpose()
    print(data)
    return data


# In[10]:


mbti_group = ['intj', 'intp', 'entj', 'entp',
              'infj', 'infp', 'enfj', 'enfp',
              'istj', 'isfj', 'estj', 'esfj',
              'istp', 'isfp', 'estp', 'esfp']


# ### 파일 저장
# 출력 결과는 한 페이지씩 테스트한 것

# In[11]:


# INFP & ENFP 게시판 크롤링, menuid=18
# data18 = crawling(18, mbti_group)
# data18.head(5)


# # In[12]:


# data18.to_pickle('menuid=18 crawling2.pkl')

# with open("./data18.pickle", "wb") as MyFile:
#    pickle.dump(data18, MyFile)


# In[13]:


# INTP & ENTP 게시판 크롤링, menuid=17
# data17 = crawling(17, mbti_group)
# data17.head(5)


# #In[14]:


# data17.to_pickle('menuid=17 crawling.pkl')

# with open("./data17.pickle", "wb") as MyFile:
#     pickle.dump(data17, MyFile)


# In[15]:


# ISFP & ESFP 게시판 크롤링, menuid=16
# data16 = crawling(16, mbti_group)
# data16.head(5)


# # In[16]:


# data16.to_pickle('menuid=16 crawling.pkl')

# with open("./data16.pickle", "wb") as MyFile:
#     pickle.dump(data16, MyFile)


# In[17]:


# ISTP & ESTP 게시판 크롤링, menuid=15
# data15 = crawling(15, mbti_group)
# data15.head(5)


# # In[18]:


# data15.to_pickle('menuid=15 crawling.pkl')

# with open("./data15.pickle", "wb") as MyFile:
#     pickle.dump(data15, MyFile)


# In[19]:


# INFJ & ENFJ 게시판 크롤링, menuid=14
# data14 = crawling(14, mbti_group)
# data14.head(5)


# # In[20]:


# data14.to_pickle('menuid=14 crawling.pkl')

# with open("./data14.pickle", "wb") as MyFile:
#     pickle.dump(data14, MyFile)


# In[21]:


# ISFJ & ESFJ 게시판 크롤링, menuid=13
data13 = crawling(13, mbti_group)
data13.head(5)


# # In[22]:


# data13.to_pickle('menuid=13 crawling.pkl')

# with open("./data13.pickle", "wb") as MyFile:
#     pickle.dump(data13, MyFile)


# In[23]:


# INTJ & ENTJ 게시판 크롤링, menuid=12
# data12 = crawling(12, mbti_group)
# data12.head(5)


# # In[24]:


# data12.to_pickle('menuid=12 crawling.pkl')

# with open("./data12.pickle", "wb") as MyFile:
#     pickle.dump(data12, MyFile)


# In[25]:


# ISTJ & ESTJ 게시판 크롤링, menuid=11
data11 = crawling(11, mbti_group)
data11.head(5)


# In[26]:


data11.to_pickle('menuid=11 crawling.pkl')

with open("./data11.pickle", "wb") as MyFile:
    pickle.dump(data11, MyFile)

