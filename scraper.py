import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import pandas as pd
from time import sleep
import sys,os
os.makedirs("data", exist_ok=True) 
def update_message(message):
    print(message,end='\r')
    sys.stdout.flush()


def page_scroll(driver):
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    try_times = 0
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollBy(0,1500)")

        # Wait to load page
        sleep(1.5)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")

        if last_height == new_height:
            try_times += 1

        if try_times > 3:
            try_times = 0
            break
        last_height = new_height


def convert_to_number(s):
    """
    Converts a string like '8.5k', '100k', or '10k' into a numeric value.

    Args:
        s (str): Input string to be converted.

    Returns:
        float: The numeric value.
    """
    if 'k' in s.lower():  # Handles 'k' (thousands)
        return float(s.lower().replace('k', '')) * 1000
    elif 'm' in s.lower():  # Handles 'm' (millions)
        return float(s.lower().replace('m', '')) * 1_000_000
    elif 'b' in s.lower():  # Handles 'b' (billions)
        return float(s.lower().replace('b', '')) * 1_000_000_000
    else:  # Handles plain numbers
        return float(s)


def scrape_product_details(driver,product_urls,index,total):
    data = []
    for index_,product in enumerate(product_urls):
        update_message(f"Progress: {index+1} out of cateogry {total} | {index_+1} out of {len(product_urls)} products")
        try:
            driver.get(product["link"])
            sleep(1.5)
        except:
            pass

        try:
            soup = bs(driver.page_source,"html.parser")
        except:
            pass
        
        try:
            productName = soup.find("span",attrs={"id":"productTitle"}).text.strip()
        except:
            productName = None

        try:
            brand = soup.find("a",attrs={"id":"bylineInfo"}).text.strip()
            brand = " ".join(brand.split())
            brand = brand.replace("Visit the","").strip().replace("Store","").strip()
        except:
            brand = None
        
        try:
            rating=soup.find('span',attrs={"data-hook":"rating-out-of-text"}).text.strip()
            rating=rating.replace('out of 5','').strip()
            rating = float(rating)
        except:
            rating=None
        try:
            no_of_reviews=soup.find('span',attrs={"data-hook":"total-review-count"}).text.strip()
            no_of_reviews=no_of_reviews.replace('global ratings','').strip().replace(",","").strip()
            no_of_reviews = int(no_of_reviews)
        except:
            no_of_reviews=None

        try:
            productId = soup.find("div",attrs={"id":"averageCustomerReviews_feature_div"}).find("div",attrs={"id":"averageCustomerReviews"})["data-asin"]
        except:
            productId = None

        try:
            purchased_in_last_month = soup.find("span",attrs={"id":"social-proofing-faceout-title-tk_bought"}).find("span",attrs={"class":"a-text-bold"}).text.strip()
            purchased_in_last_month = purchased_in_last_month.split("+")[0].strip()
            purchased_in_last_month = convert_to_number(purchased_in_last_month)
        except:
            purchased_in_last_month = None

        sales_rank_in_parent_category, sales_rank_in_sub_category = None, None
        parent_category, sub_category = None, None
        country_of_origin, release_date = None, None

        try:
            not_table_form_details = soup.find("div",attrs={"id":"detailBulletsWrapper_feature_div"})
        except:
            not_table_form_details = None
        if not_table_form_details is None:
            try:
                tr_tags = soup.find("div",attrs={"id":"prodDetails"}).find_all("tr")
                for tr_tag in tr_tags:
                    key_text = tr_tag.find("th").text.strip()
                    key_text = " ".join(key_text.split())

                    value_text = tr_tag.find("td").text.strip()
                    value_text = " ".join(value_text.split())
                    
                    if "Date First Available" in key_text or "Release Date" in key_text:
                        release_date=value_text
                    elif "Country of Origin" in key_text:
                        country_of_origin = value_text
                    elif "Best Sellers Rank" in key_text or "BestSellersRank" in key_text:
                        sales_rank_in_parent_category = int(value_text.split("(")[0].strip().split(" in ")[0].strip().replace("#","").strip())
                        parent_category = value_text.split("(")[0].strip().split(" in ")[-1].strip()

                        sales_rank_in_sub_category = int(value_text.split(")")[-1].strip().split(" in ")[0].strip().replace("#","").strip())
                        sub_category = value_text.split(")")[-1].strip().split(" in ")[-1].strip()
                        if "#" in sub_category:
                            sub_category = sub_category.split("#")[0].strip()
            except:
                pass
        else:
            try:
                span_tags = not_table_form_details.find_all("span",attrs={"class":"a-list-item"})
                for span_tag in span_tags:
                    key_text = span_tag.find("span",attrs={"class":"a-text-bold"}).text.strip()
                    key_text = " ".join(key_text.split())

                    value_text = span_tag.find_all("span")[1].text.strip()
                    value_text = " ".join(value_text.split())
                    
                    if "Date First Available" in key_text or "Release Date" in key_text:
                        release_date=value_text
                    elif "Country of Origin" in key_text:
                        country_of_origin = value_text
                    elif "Best Sellers Rank" in key_text or "BestSellersRank" in key_text:
                        value_text = span_tag.text.strip()
                        value_text = " ".join(value_text.split())
                        value_text = value_text.split(":")[-1].strip()
                        sales_rank_in_parent_category = int(value_text.split("(")[0].strip().split(" in ")[0].strip().replace("#","").strip())
                        parent_category = value_text.split("(")[0].strip().split(" in ")[-1].strip()

                        sales_rank_in_sub_category = int(value_text.split(")")[-1].strip().split(" in ")[0].strip().replace("#","").strip())
                        sub_category = value_text.split(")")[-1].strip().split(" in ")[-1].strip()
                        if "#" in sub_category:
                            sub_category = sub_category.split("#")[0].strip()
            except:
                pass

        
        if country_of_origin is None or release_date is None:
            try:
                div_tags = soup.find_all("div",attrs={"class":"product-facts-detail"})
                for div_tag in div_tags:
                    key_text = div_tag.find("div",attrs={"class":"a-fixed-left-grid-col a-col-left"}).text.strip()
                    key_text = " ".join(key_text.split())

                    value_text = div_tag.find("div",attrs={"class":"a-fixed-left-grid-col a-col-right"}).text.strip()
                    value_text = " ".join(value_text.split())
                    
                    if ("Date First Available" in key_text or "Release Date" in key_text) and release_date is None:
                        release_date=value_text
                    elif "Country of Origin" in key_text and country_of_origin is None:
                        country_of_origin = value_text
            except:
                pass

        data.append(
            {
                "Product Url":product["link"],
                "Product Name":productName,
                "Brand": brand,
                "Product ID": productId,
                "Price": product["price"],
                "Rating": rating,
                "Number of Reviews":no_of_reviews,
                "Parent Category":parent_category,
                "Sub Category": sub_category,
                "Sales Rank(in parent category)":sales_rank_in_parent_category,
                "Sales Rank(in sub category)":sales_rank_in_sub_category,
                "Release Date": release_date,
                "Country of Origin":country_of_origin,
                "Purchased in Last Month":purchased_in_last_month
            }
        )


    return data


def get_data(driver,category_urls,total):
    product_details_data = []
    for index, cate_url in enumerate(category_urls):
        update_message(f"Progress: {index+1} out of cateogry {total} | 0 out of 0 products")
        product_urls = []
        page_url = cate_url
        while True:
            try:
                driver.get(page_url)
                sleep(3)
            except:
                pass
            page_scroll(driver)
            # with open(f"../data/page{index}.html","w",encoding="utf-8") as f:
            #     f.write(driver.page_source)
            try:
                div_tags = bs(driver.page_source,"html.parser").find_all("div",attrs={"class":"zg-grid-general-faceout"})
                for div_tag in div_tags:
                    link = div_tag.find("a",attrs={"class":"a-link-normal aok-block", "role":"link"})["href"]
                    # print("link:",link)
                    try:
                        price = div_tag.find("span",attrs={"class":"a-size-base a-color-price"}).text.strip()
                        price = price.replace("$","").strip()
                        price = float(price)
                    except:
                        price = None
                    if price is None:
                        try:
                            price = div_tag.find("span",attrs={"class":"a-color-secondary"}).text.strip()
                            price = price.split("$")[-1].strip()
                            price = float(price)
                        except:
                            price = None
                    
                    product_urls.append({"link":f"https://www.amazon.com{link}","price":price})
            except:
                pass
            try:
                next_page_link = bs(driver.page_source,"html.parser").find("li",attrs={"a-last"}).find("a")["href"]
                page_url = f"https://www.amazon.com{next_page_link}"
            except:
                break
        if len(product_urls)==0:
            print("\nProducts not found!\n")
            input("Press Enter key to continue........")
        data_lists = scrape_product_details(driver,product_urls,index,total)
        if len(data_lists)!=0:
            product_details_data.extend(data_lists)

    return product_details_data





def main():
    url = "https://www.amazon.com/Best-Sellers/zgbs/"

    driver = uc.Chrome()

    try:
        driver.get(url)
        sleep(3)
    except:
        pass

    page_scroll(driver)
    # with open(r"D:\DS-Course\projects\Trending Products on E-Commerce Website\data\page.html","w",encoding="utf-8") as f:
    #     f.write(driver.page_source)
    category_urls = []
    try:
        a_tags = bs(driver.page_source, "html.parser").find_all("a", string="See More", attrs={"class": "a-link-normal"})
        for a_tag in a_tags:
            category_urls.append(f"https://www.amazon.com{a_tag['href']}")
    except:
        pass
    total = len(category_urls)
    print("total category URL: ",total,"\n")
    
    product_data = get_data(driver,category_urls,total)

    df = pd.DataFrame(product_data)
    # df.to_excel("../data/Amazon Best Sellers.xlsx",index=False)
    df.to_csv("../data/raw_data.csv",index=False)

    driver.quit()





if __name__ == "__main__":
    main()





