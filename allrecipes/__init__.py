# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup

import urllib.parse
import urllib.request

import re


class AllRecipes(object):

	@staticmethod
	def search(query_dict):
		"""
		Search recipes parsing the returned html data.
		"""
		base_url = "https://allrecipes.com/search/results/?"
		query_url = urllib.parse.urlencode(query_dict)

		url = base_url + query_url

		req = urllib.request.Request(url)
		req.add_header('Cookie', 'euConsent=true')

		html_content = urllib.request.urlopen(req).read()

		soup = BeautifulSoup(html_content, 'html.parser')

		search_data = []
		articles = soup.select("div.component.card")

		iterarticles = iter(articles)

		for article in iterarticles:
			data = {}
			try:
				data["name"] = article.find("h3", {"class": "card__title"}).get_text().strip(' \t\n\r')
				data["description"] = article.find("div", {"class": "card__summary"}).get_text().strip(' \t\n\r')
				data["url"] = article.find("a", href=re.compile('^https://www.allrecipes.com/recipe/'))['href']
				try:
					data["image"] = article.find("img", src=re.compile('^https://'))
				except Exception as e1:
					pass

				try:
					data["rating"] = article.find("span", class_="review-star-text").get_text()
				except ValueError:
					data["rating"] = None

				try:
					data["ratings-count"] = float(article.find("span", {"class": "ratings-count"}).get_text())
				except ValueError:
					data["ratings-count"] = None
			except Exception as e2:
				pass
			#if data and "image" in data:  # Do not include if no image -> its probably an add or something you do not want in your result
			search_data.append(data)

		return search_data

	@staticmethod
	def get(url):
		"""
		'url' from 'search' method.
		 ex. "/recipe/106349/beef-and-spinach-curry/"
		"""
		#base_url = "https://allrecipes.com/"
		#url = base_url + uri

		req = urllib.request.Request(url)
		req.add_header('Cookie', 'euConsent=true')

		html_content = urllib.request.urlopen(req).read()
		soup = BeautifulSoup(html_content, 'html.parser')

		try:
			rating = float(soup.find("span", {"class": "recipe-reviews-decimal-avg"}).get_text())
		except ValueError:
			rating = None
		
		ingredients = soup.find_all("li", class_="ingredients-item")
		steps = soup.find_all("li", {"class": "instructions-section-item"})

		name = soup.find("h1", {"class": "headline"}).get_text().replace("®", "")

		recipe_properties = soup.find("section", {"class": "recipe-meta-container"})

		prep_time = recipe_properties.find("div", text="prep:").find_next_sibling('div').get_text()
		cook_time = recipe_properties.find("div", text="cook:").find_next_sibling('div').get_text()
		total_time = recipe_properties.find("div", text="total:").find_next_sibling('div').get_text()
		servings = recipe_properties.find("div", text="Servings:").find_next_sibling('div').get_text()

		data = {
				"rating": rating,
				"ingredients": [],
				"steps": [],
				"name": name,
				"prep_time": prep_time,
				"cook_time": cook_time,
				"total_time": total_time,
				"servings": servings
				}

		for ingredient in ingredients:
			str_ing = ingredient.find("span", {"class": "ingredients-item-name"}).get_text()
			if str_ing and str_ing != "Add all ingredients to shopping list":
				data["ingredients"].append(str_ing)

		for step in steps:
			str_step = step.find("p").get_text()
			if str_step:
				data["steps"].append(str_step)

		return data