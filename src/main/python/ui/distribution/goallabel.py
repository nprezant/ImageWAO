from PySide2 import QtWidgets


class GoalLabel(QtWidgets.QLabel):
    """Convenience class for describing the goal
    number of photos per person.
    """

    def __init__(self):
        super().__init__()
        sizePolicy: QtWidgets.QSizePolicy = self.sizePolicy()
        sizePolicy.setVerticalPolicy(QtWidgets.QSizePolicy.Maximum)
        self.setSizePolicy(sizePolicy)
        self.setToolTip(
            "Drag and drop transects from one person to another"
            " to create the perfect balance among your team.\n"
            " In an ideal world, all members would have the same number"
            " of photos to go through.\nHowever, since the photos are grouped"
            " by transect, this cannot always be achieved."
        )

    def setGoal(self, goal: int):
        self.setText(f"The goal number of photos per person is {goal}.")
