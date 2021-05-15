import pomace


page = pomace.visit("https://www.wikipedia.org/")

page.fill_search("page object model")
page = page.click_search()

print(page.title)
