import datetime


class Timeline:
    def __init__(self, projects_list):
        self.projects_list = projects_list
        self.first_date, self.last_date = self.find_first_and_last_dates()

    def generate_timeline(self):
        current_date = self.first_date
        dates = []
        while self.last_date >= current_date:
            dates.append(current_date)
            current_date += datetime.timedelta(days=1)
        return dates

    def find_first_and_last_dates(self):
        if self.projects_list:
            first_date = datetime.date.fromisoformat(self.projects_list[0][2])
            last_date = datetime.date.fromisoformat(self.projects_list[0][3])
            for project in self.projects_list:
                if first_date > datetime.date.fromisoformat(project[2]):
                    first_date = datetime.date.fromisoformat(project[2])
                if last_date < datetime.date.fromisoformat(project[3]):
                    last_date = datetime.date.fromisoformat(project[3])
            if last_date - first_date < datetime.timedelta(days=28):
                last_date = first_date + datetime.timedelta(days=28)
        else:
            first_date = datetime.date.today() - datetime.timedelta(days=14)
            last_date = datetime.date.today() + datetime.timedelta(days=14)
        return first_date, last_date


if __name__ == "__main__":
    t = Timeline(datetime.date.today(), "2020-11-29")
    print(t.generate_timeline())