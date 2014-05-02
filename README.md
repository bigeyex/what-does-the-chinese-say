# what's this
**What does Chinese say** allows you to search among Chinese news and social media (weibo).

It uses Baidu translation API, so you can search in English and view results (machine-translated) in English.

## A disclaimer

This service uses machine translating. You know, it's unrelialble. The translated content may not reflect the original ideal or intent of the content's author. I, or anybody who set up this server, will be not responsible for the translated content and any potential consequences following that. Use the data with discretion, and always read the source material with someone who understands Chinese before publishing any derived work.

Also, **What appears in the results is not THE EXACT VIEWPOINT of 1.3 billion people in China, nor is its any collective representation**. As you can see from the data source section, data come from Baidu search engine. They have their own *data gathering 

## Set up your own server
Step 1: Have Flask and BeautifulSoup and sqlite3 installed.

Step 2: Clone the code

Step 3: python main.py.

Step 4: (Recommended) Register a api from 
http://developer.baidu.com/
Create an app and copy the client_id to the beginning of main.py (replace the string after translation_client_id). 

## Then why do you make this?

When I came to US, I started to read news about China through Associated Press, Foreign Policy, and websites such as Tea Leaf Nation. I found that people here are really curious about opinions of Chinese people (especially Chinese "Netizen") in some topics. However, it is funny to see that most of the information people here can get about China come from several "China experts", who delicately tailor the information - not too spicy, not too weak. 

Therefore I made this tool, which allows you to "talk" directly to Chinese people (?, remember the disclaimer?). You can also continue the dailogue by following the links it provided in the search results.

## Who is this made for?

**Journalists**. They can explore the topics they are interested in and use the result as a start point of follow-up research. Information from Chinese news media, blogs, forums, and Weibo (Chinese twitter) helps journalists to find new opportunities and achieve a balanced view. 

**Media Hackers.** This tool provide a JSON interface, with which hackers can remix the data with something else. Want to see a comparision of views between Chinese and Americans? Want to see how attention of Chinese people on specific topic shifted? Code it out!

**Just for fun.** What do people say about Obama? What do Chinese say about a company? Find your question and get answers from 1.3b people who lives thousands of miles away.

## Your data source?

Ok, it comes to tech details.
All the data came from Baidu news search engine. Including news, forum posts, blogs, and tweets. 

I use Baidu Translation API to translate the keywords and results. This uses an API key, so when it's out of quota you can apply a new one at http://developer.baidu.com/ 

Here a description of each source (in my opinion):

**News**: mainstream, well-written, well-censored news from various Chinese news websites. Notice that most Chinese websites are not allowed to publish their own news. So the news you see here are probably come from paper-based media.

**Blogs**: Chinese blogs, mostly hosted on blog platforms such as Sina or Netease. Though they are not as popular as "micro-blogging (Twitter)" now.

**Forum**: Forum posts across websites. Note that Baidu Tieba (One of the most widely used forum in China) is not included in the results. Remember the disclaimer?

**Weibo**: "Chinese Twitter". The user base is declining but still considerable, and more heavily used than all other sources by native Chinese. Where do people go? A new private media called "Wechat".