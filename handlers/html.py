from bs4 import BeautifulSoup
import os

def parse_html(file):
    try:
        with open(file, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()
    except Exception as e:
        print(f"Error reading html file: {e}")
        return []

    soup = BeautifulSoup(source, "html.parser")

    info = soup.select_one("p#info")
    mg_info = soup.select_one("p[style='text-align:center;font-size:30;color:Blue']")
    buttons_soup = soup.select("button.collapsible")
    paras_soup = soup.select("p")[2:] if len(soup.select("p")) > 2 else []
    
    videos = []
    if info is not None:
        all_videos_soup = soup.select_one("div#videos")
        if all_videos_soup:
            topics_soup = all_videos_soup.select("div.topic")
            for topic_soup in topics_soup:
                videos_soup = topic_soup.select("p.video")
                for video_soup in videos_soup:
                    v_elem = video_soup.select_one("span.video_name")
                    video_name = v_elem.get_text(strip=True) if v_elem else "Video"
                    a_elem = video_soup.select_one("a")
                    video_link = a_elem.get_text(strip=True) if a_elem else ""
                    if not (video_link.startswith("http://") or video_link.startswith("https://")):
                        continue
                    videos.append(f"{video_name.replace(':', '')}:{video_link}".split(':', 1))
    elif mg_info is not None and len(buttons_soup) != 0:
        for button_soup in buttons_soup:
            content_div = button_soup.find_next_sibling("div", class_="content")
            if content_div and content_div.p:
                para = content_div.p
                for a_soup in para.select("a"):
                    br = a_soup.find_previous_sibling()
                    if br:
                        br.decompose()
                    video_name = a_soup.previousSibling or "Video"
                    video_link = a_soup.get_text(strip=True)
                    if not (video_link.startswith("http://") or video_link.startswith("https://")):
                        continue
                    videos.append(f"{str(video_name).replace(':', '')}:{video_link}".split(':', 1))
    elif mg_info is not None and len(paras_soup) > 0 and paras_soup[0].b is not None:
        for topic_para in paras_soup:
            if paras_soup.index(topic_para) % 2 == 0:
                para = topic_para.find_next_sibling("p")
                if para:
                    for a_soup in para.select("a"):
                        br = a_soup.find_previous_sibling()
                        if br:
                            br.decompose()
                        video_name = a_soup.previousSibling or "Video"
                        video_link = a_soup.get_text(strip=True)
                        if not (video_link.startswith("http://") or video_link.startswith("https://")):
                            continue
                        videos.append(f"{str(video_name).replace(':', '')}:{video_link}".split(':', 1))
    elif mg_info is not None and len(paras_soup) > 0 and paras_soup[0].get("style") == "text-align:center;font-size:25px;":
        for para in paras_soup:
            video_name = para.contents[0] if para.contents else "Video"
            a_elem = para.select_one("a")
            video_link = a_elem.get_text(strip=True) if a_elem else ""
            if not (video_link.startswith("http://") or video_link.startswith("https://")):
                continue
            videos.append(f"{str(video_name).replace(':', '')}:{video_link}".split(':', 1))
    else:
        for a_soup in soup.select("a"):
            video_link = a_soup.get("href") or a_soup.get_text(strip=True)
            video_name = a_soup.get_text(strip=True) or "Video"
            if not (video_link.startswith("http://") or video_link.startswith("https://")):
                continue
            videos.append(f"{str(video_name).replace(':', '')}:{video_link}".split(':', 1))
    
    return videos
