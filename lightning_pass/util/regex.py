"""Module with regular expressions."""
import re

USERNAME = re.compile(r"^\w{5,}$")
PASSWORD = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[\d])(?=.*[^\w])\S{8,}$")

EVENT_SEARCH = re.compile(r".+(?=_event)")
