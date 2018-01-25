class Model:
    def __init__(self):
        """
        Initialize Model object
        """
        self.name = "model"

    def predict(self, preferences):
        """
        Return 5 podcasts based on user input
        """
        predictions = ["Comedy Bang Bang", "This American Life",
                       "Reply All", "On The Media"]
        return predictions
