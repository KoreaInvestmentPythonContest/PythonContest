from main import *

import sys

class Ui_class():
    def __init__(self):
        print("Ui_class 입니다")
        self.KoreaInvestment = KoreaInvestment()
        self.KoreaInvestment.function_start()


if __name__ == "__main__":
    ui_class =Ui_class()