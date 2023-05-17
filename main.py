from loop import Loop

# Entry point
if __name__ == '__main__':
    Loop().run(desired_number=150,
               population_size=8,
               cross_range=1,
               sleep=1)
