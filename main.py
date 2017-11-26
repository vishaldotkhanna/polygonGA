from helper_classes import Population, initialize_global_vars, Genotype
from upload_service import upload_file

from os import getcwd
from PIL import Image, ImageFilter
from copy import deepcopy


IMAGE_PATH = 'pepsi.png'
SAVE_PATH = getcwd() + '/img_generate_heroku'
SAVE_TO_DROPBOX = True
SAVE_FREQUENCY = 5


def scm():
    current_population = Population()
    current_population.generate_initial()

    generation_index = 1
    last_change = 0
    while True:
        print 'Computing over generation: {}'.format(generation_index)
        new_population = deepcopy(current_population)
        parents = new_population.select_parents()
        new_population.crossover(parents)
        new_population.mutate()
        new_population.elitism()

        if new_population.get_best_fitness() < current_population.get_best_fitness():
            current_population = new_population
            last_change = generation_index

        if not generation_index % SAVE_FREQUENCY and (generation_index - last_change) < SAVE_FREQUENCY:
            print 'Saving image "generation_{}.png"'.format(generation_index)
            current_image = current_population.genotypes[current_population.get_best()].get_image()
            filtered_image = current_image.filter(ImageFilter.GaussianBlur(radius=3))
            filtered_image.save(SAVE_PATH + '/generation_{}.png'.format(generation_index))
            if SAVE_TO_DROPBOX:
                upload_file('generation_{}.png'.format(generation_index))
                upload_file('fitness_log.txt', use_base_path=False)

        fitness_list = [round(g.get_fitness(), 3) for g in current_population.genotypes]
        log_message = 'generation: {}, fitness: {}\ngenerations since last update {}\n\n'\
            .format(generation_index, str(fitness_list), generation_index - last_change)
        print log_message
        with open('fitness_log.txt', 'a') as f:
            f.write(log_message)
        generation_index += 1


def simple_ga():
    parent = Genotype()
    parent.generate()

    generation_index = 1
    last_change = 0
    while True:
        child = deepcopy(parent)
        child.mutate()
        if child.get_fitness() < parent.get_fitness():
            parent = child
            last_change = generation_index

        if not generation_index % SAVE_FREQUENCY and (generation_index - last_change) < SAVE_FREQUENCY:
            print 'Saving image "generation_{}.png"'.format(generation_index)
            current_image = parent.get_image()
            filtered_image = current_image.filter(ImageFilter.GaussianBlur(radius=3))
            filtered_image.save(SAVE_PATH + '/generation_{}.png'.format(generation_index))
            if SAVE_TO_DROPBOX:
                upload_file('generation_{}.png'.format(generation_index))
                upload_file('fitness_log.txt', use_base_path=False)

        log_message = 'Generation: {}\nFitness: {}\nGenerations since last change: {}\n\n'\
            .format(generation_index, round(parent.get_fitness(), 3), (generation_index - last_change))

        print log_message
        with open('fitness_log.txt', 'a') as f:
            f.write(log_message)
        generation_index += 1


if __name__ == '__main__':
    image = Image.open(IMAGE_PATH)
    initialize_global_vars(image)
    simple_ga()
    # scm()