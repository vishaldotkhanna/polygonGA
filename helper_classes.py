from random import randrange, uniform, shuffle, random, sample
from math import sqrt
import numpy as np
from PIL import Image, ImageDraw

POPULATION_SIZE = 10
NUMBER_OF_POLYGONS = 50
MIN_VERTICES = 3
MAX_VERTICES = 5
NUMBER_OF_PARENTS = 4
ELITISM_NUMBER = 4    # Number of fittest genotypes to carry to the next generation directly.
OFFSET = 10
PROBABILITY_MUTATION = 0.3

INPUT_IMAGE = None
IMAGE_WIDTH = 0
IMAGE_HEIGHT = 0
IMAGE_MATRIX = None
MAX_DELTA = 0


class Polygon:
    def __init__(self):
        self.color = [255, 255, 255, 255]
        self.vertices = []

    def generate(self, vertices=True, color=True, randomize_color=False):
        if color and randomize_color:
            self.color = generate_color()
        if vertices:
            self.vertices = []    # To handle mutation.
            for i in range(randrange(MIN_VERTICES, MAX_VERTICES + 1)):
                self.vertices.append(generate_point(IMAGE_WIDTH, IMAGE_HEIGHT))

    def mutate(self):
        rand = random() < 0.5
        self.generate(vertices=rand, color=not rand, randomize_color=True)    # Mutate either color or vertices.


class Genotype:
    def __init__(self):
        self.polygons = []
        self.fitness = -1
        self.image = None

    def generate(self):
        for i in range(NUMBER_OF_POLYGONS):
            new_polygon = Polygon()
            new_polygon.generate()
            self.polygons.append(new_polygon)

    def get_fitness(self):
        if self.fitness == -1:
            self.compute_fitness()
        return self.fitness

    def compute_fitness(self):
        if self.image is None:
            self.generate_image()

        # delta_matrix = np.subtract(IMAGE_MATRIX, np.array(self.image))
        # self.fitness = sqrt(np.sum(np.square(delta_matrix)))

        self.fitness = get_image_error(self.image)

    def get_image(self):
        if self.image is None:
            self.generate_image()

        return self.image

    def generate_image(self):
        image = Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT), color=(0, 0, 0, 255))
        draw_image = Image.new('RGBA', (IMAGE_WIDTH, IMAGE_HEIGHT))
        draw = ImageDraw.Draw(draw_image)

        for polygon in self.polygons:
            draw.polygon(make_tuple(polygon.vertices), fill=tuple(polygon.color), outline=tuple(polygon.color))
            image.paste(draw_image, mask=draw_image)

        self.image = image

    def mutate(self):
        # for polygon in self.polygons:
        #     if random() < PROBABILITY_MUTATION:
        #         polygon.mutate()

        self.polygons[randrange(0, NUMBER_OF_POLYGONS)].mutate()

        self.fitness = -1   # Resetting fitness since the genotype has been mutated.
        self.image = None


class Population:
    def __init__(self):
        self.genotypes = []

    def generate_initial(self):
        for i in range(POPULATION_SIZE):
            member = Genotype()
            member.generate()
            self.genotypes.append(member)

    def select_parents(self):   # Stochastic Universal Sampling
        total_fitness = self.compute_total_fitness()
        point_distance = total_fitness / NUMBER_OF_PARENTS
        start_point = uniform(0, point_distance)
        points = [start_point + i * point_distance for i in range(NUMBER_OF_PARENTS)]

        parents = set()
        while len(parents) < NUMBER_OF_PARENTS:
            shuffle(self.genotypes)
            i = 0
            while i < len(points) and len(parents) < NUMBER_OF_PARENTS:
                j = 0
                while j < len(self.genotypes):
                    if self.get_subset_sum(j) > points[i]:
                        parents.add(self.genotypes[j])
                        break
                    j += 1
                i += 1

        return list(parents)

    def compute_total_fitness(self):
        # total_fitness = 0
        # for member in self.genotypes:
        #     total_fitness += member.get_fitness()
        # return total_fitness

        f = lambda geno: sum([member.get_fitness() for member in geno])
        return f(self.genotypes)

    def crossover(self, parents):
        shuffle(parents)
        for i in range(0, NUMBER_OF_PARENTS, 2):
            parents[i], parents[i + 1] = self.generate_crossover_children(parents[i], parents[i + 1])

    def generate_crossover_children(self, parent_1, parent_2):    # Single Point Crossover
        crossover_point = randrange((4 * NUMBER_OF_POLYGONS) / 10, (6 * NUMBER_OF_POLYGONS) / 10 + 1)
        child_1, child_2 = Genotype(), Genotype()
        f = lambda par, child, i: child.polygons.append(par.polygons[i])
        for i in range(crossover_point):
            f(parent_1, child_1, i)
            f(parent_2, child_2, i)
        for i in range(crossover_point, NUMBER_OF_POLYGONS):
            f(parent_1, child_2, i)
            f(parent_2, child_1, i)
        child_1.mutate()
        child_2.mutate()
        return child_1, child_2

    def mutate(self):
        for genotype in self.genotypes:
            if random() < PROBABILITY_MUTATION:
                genotype.mutate()

    def elitism(self):
        # 8 fittest genotypes are carried forward to the next generation. The remaining members are randomly chosen.
        self.genotypes.sort(key=lambda f: f.get_fitness(), reverse=False)
        self.genotypes = self.genotypes[:ELITISM_NUMBER] + sample(self.genotypes[ELITISM_NUMBER:], POPULATION_SIZE - ELITISM_NUMBER)

    def get_subset_sum(self, end, start=0):
        subset_sum, i = 0.0, start
        while i <= end:
            subset_sum += self.genotypes[i].get_fitness()
            i += 1
        return subset_sum

    def get_best(self):
        return np.argmin([g.get_fitness() for g in self.genotypes])

    def get_best_fitness(self):
        return min([g.get_fitness() for g in self.genotypes])


def generate_color():
    return [randrange(0, 256) for i in range(4)]


def generate_point(x_max, y_max):   # Include offset.
    x, y = randrange(0, x_max + 1), randrange(0, y_max + 1)
    return [x, y]


def make_tuple(vertices):
    return [tuple(vertex) for vertex in vertices]


def get_image_error(image1):
    error = 0.0
    for x in range(IMAGE_WIDTH):
        for y in range(IMAGE_HEIGHT):
            # rgb1, rgb2 = image1.getpixel((x, y)), image2.getpixel((x, y))
            rgb1, rgb2 = image1.getpixel((x, y)), IMAGE_MATRIX[x][y]
            delta = 0.0
            for i in range(3):
                delta += pow(rgb1[i] - rgb2[i], 2)
            error += float(sqrt(delta))

    return error


def initialize_global_vars(image):
    global INPUT_IMAGE, IMAGE_WIDTH, IMAGE_HEIGHT, IMAGE_MATRIX
    INPUT_IMAGE = image
    IMAGE_WIDTH, IMAGE_HEIGHT = image.size
    IMAGE_MATRIX = []
    for x in range(IMAGE_WIDTH):
        current_row = []
        for y in range(IMAGE_HEIGHT):
            current_row.append(INPUT_IMAGE.getpixel((x, y)))
        IMAGE_MATRIX.append(current_row)

