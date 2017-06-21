import requests
from bs4 import BeautifulSoup
import json
from textblob import TextBlob
from nltk.tokenize import LineTokenizer
import csv

token = ""
base_url = "http://api.genius.com"

def input_info():
	artist_name = input("Artist: ")
	song_title = input("Title: ")
	if artist_name and song_title:
		query(artist_name, song_title)

def query(artist_name, song_title):
	print("querying")
	search_url = base_url + "/search?q=" + artist_name + " - " + song_title
	headers = {'Authorization': 'Bearer ' + token}
	response = requests.get(search_url, headers = headers)
	json = response.json()
	song_info = None
	for hit in json["response"]["hits"]:
		print("iterating through hits")
		if hit["result"]["primary_artist"]["name"] == artist_name:
			song_info = hit
			print("Success!")
			break
		else:
			print("Not found. Try again?")
	if song_info:
		song_api_path = song_info["result"]["api_path"]
		get_song_info(song_api_path, headers)
	else:
		input_info()

def get_song_info(song_api_path, headers):
	song_url = base_url + song_api_path
	response = requests.get(song_url, headers = headers)
	json = response.json()
	song_id = json["response"]["song"]["id"]
	writers = []
	for names in json["response"]["song"]["writer_artists"]:
		writers.append(names["name"])
	song_page_path = json["response"]["song"]["path"]
	lyrics = get_lyrics(song_page_path, headers)
	process_data(lyrics, writers, song_id)

def get_lyrics(song_path, headers):
	print("retrieving lyrics")
	page_url = "http://genius.com" + song_path
	page = requests.get(page_url)
	html = BeautifulSoup(page.text, "html.parser")
	lyrics = html.find("div", class_="lyrics").get_text()
	print("Success!")
	return lyrics

def process_data(lyrics, writers, song_id):
	artist_gender = get_artist_gender()
	writer_gender = get_writer_gender(writers)
	row = [song_id, artist_gender, writer_gender]
	row += count_words(lyrics)
	dump_csv(row)

def get_artist_gender():
	return input("Is the artist [M]ale, [F]emale, or mi[X]ed? ")

def get_writer_gender(writers):
	print("The writer(s) of this song: " + str(writers))
	return input("Are they [M]ale, [F]emale, or mi[X]ed? ")

def count_words(lyrics):
	num_I = 0
	num_me = 0
	sub_you = 0
	obj_you = 0
	num_she = 0
	num_he = 0
	num_her = 0
	num_him = 0
	num_girl = 0
	num_boy = 0
	num_woman = 0
	num_man = 0
	num_my = 0
	tokenizer = LineTokenizer()
	blob = TextBlob(lyrics, tokenizer = tokenizer)
	k = 0
	for i in blob.tokens:
		new_blob = TextBlob(i).lower()
		print(new_blob.tags)
		for j in new_blob.words:
			j.lemmatize()
			if j == "i":
				num_I += 1
			elif j == "me":
				num_me += 1
			elif j == "you":
				print("Line " + str(k) + ": " + str(i))
				ans = input("Is this 'you' in the [s]ubject or the [o]bject position? ")
				if ans == 's':
					sub_you += 1
				elif ans == 'o':
					obj_you += 1
			elif j == "she":
				num_she += 1
			elif j == "he":
				num_he += 1
			elif j == "her":
				print("Line " + str(k) + ": " + str(i))
				ans = input("Is this 'her' an object? [y/n] ")
				if ans == 'y':
					num_her += 1
			elif j == "him":
				num_him += 1
			elif j == "girl":
				num_girl += 1
			elif j == "boy":
				num_boy += 1
			elif j == "woman":
				num_woman += 1
			elif j == "man":
				num_man += 1
			elif j == "my" or j == "mine":
				num_my += 1
			else:
				pass
		k += 1
	counts = [num_I, num_me, num_my, sub_you, obj_you, num_she, num_he, num_her, num_him, num_girl, num_boy, num_woman, num_man]
	return(counts)

def dump_csv(data):
	print("writing to CSV file")
	with open('data.csv', 'a') as f:
		f_writer = csv.writer(f)
		f_writer.writerow(data)
	print("Finished!")
	ans = input("Would you like to query another song? [y/n] ")
	if ans == 'y':
		input_info()
	else:
		print("Quitting.")

if __name__ == "__main__":
	input_info()