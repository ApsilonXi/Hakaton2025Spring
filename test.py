from flask import Flask, render_template, redirect, url_for, request, flash, session
from scripts_bd.db_methods import *
 # Важно использовать надежный ключ в продакшене
DB = NewsDB(password="password")

print(DB.get_published_news())
