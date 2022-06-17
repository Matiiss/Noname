#include <Python.h>
#include <stdio.h>
#include <math.h>

#define len(x)  (sizeof(x) / sizeof((x)[0]))


struct Vector2 {
	double x;
	double y;
};


//int collides(int width, int height, int collision_map[height][width], int x, int y) {
	//return collision_map[y][x];
//}


struct Vector2 from_angle(double angle, struct Vector2 position, float max_distance, int width, int height, int *collision_map, int tile_size) {
	struct Vector2 direction = {cos(angle), -sin(angle)};
	double x_component = 0, y_component = 0;
	
	if (direction.x) {
		x_component = sqrt(1 + pow(direction.y / direction.x, 2));
	};
	if (direction.y) {
		y_component = sqrt(1 + pow(direction.x / direction.y, 2));
	};
	
	struct Vector2 step_size = {x_component, y_component};
	struct Vector2 tile = {(int)(position.x / tile_size) * tile_size, (int)(position.y / tile_size) * tile_size};
	struct Vector2 step, ray_length;
	
	if (direction.x < 0) {
		step.x = -1;
		ray_length.x = (position.x - (double)tile.x) * step_size.x;
	} else {
		step.x = 1;
		ray_length.x = ((double)tile.x + 1 - position.x) * step_size.x;
	};
	
	if (direction.y < 0) {
		step.y = -1;
		ray_length.y = (position.y - (double)tile.y) * step_size.y;
	} else {
		step.y = 1;
		ray_length.y = ((double)tile.y + 1 - position.y) * step_size.y;
	};
	
	
	int tile_found = 0;
	float distance = 0;
	int failsafe_counter = 0;
	
	while (!tile_found == 1 && distance < max_distance) {
		if (ray_length.x < ray_length.y || !direction.y && direction.x) {
			tile.x += step.x;
			distance = ray_length.x;
			ray_length.x += step_size.x;
		} else {
			tile.y += step.y;
			distance = ray_length.y;
			ray_length.y += step_size.y;
		};
		if (tile.x >= 0 && tile.x < width * tile_size && tile.y >= 0 && tile.y < height * tile_size) {
			tile_found = collision_map[(int)(tile.y / tile_size) * width + (int)(tile.x / tile_size)];
		};
		
		failsafe_counter++;
		if (failsafe_counter > 10000) {
			printf("Ooopsie! Failsafe activated in dda.c in from_angle!");
			break;
		}
	};
	
	struct Vector2 end = {position.x + direction.x * distance, position.y + direction.y * distance};
	
	return end;
}


static PyObject *method_from_angle(PyObject *self, PyObject *args) {
	double angle, x, y;
	int tile_size;
	float max_distance;
	PyObject *collision_map;
	
	if(!PyArg_ParseTuple(args, "dddfOi", &x, &y, &angle, &max_distance, &collision_map, &tile_size)) {
        return NULL;
    };
	
	int height = PyObject_Length(collision_map);
	int width = PyObject_Length(PyList_GetItem(collision_map, 0));
	
	int *collision_array = malloc(height * width * sizeof(int));
	
	for (int row_num = 0; row_num < height; row_num++) {
		PyObject *row = PyList_GetItem(collision_map, row_num);
		for (int col_num = 0; col_num < width; col_num++) {
			PyObject *value = PyList_GetItem(row, col_num);
			collision_array[row_num * width + col_num] = (int)PyLong_AsLong(value);
		};
	};
	
	struct Vector2 start_position = {x, y};
	struct Vector2 end_point = from_angle(
		angle, 
		start_position, 
		max_distance,
		width, 
		height, 
		collision_array, 
		tile_size
	);
	
	free(collision_array);
	
	return Py_BuildValue("ii", round(end_point.x), round(end_point.y));
}


static PyObject *method_from_angle_range(PyObject *self, PyObject *args) {
	double x, y, start, stop, step;
	int tile_size;
	float max_distance;
	PyObject *collision_map;
	
	if(!PyArg_ParseTuple(args, "dddddfOi", &x, &y, &start, &stop, &step, &max_distance, &collision_map, &tile_size)) {
        return NULL;
    };
	
	int height = PyObject_Length(collision_map);
	int width = PyObject_Length(PyList_GetItem(collision_map, 0));
	
	int *collision_array = malloc(height * width * sizeof(int));
	
	for (int row_num = 0; row_num < height; row_num++) {
		PyObject *row = PyList_GetItem(collision_map, row_num);
		for (int col_num = 0; col_num < width; col_num++) {
			PyObject *value = PyList_GetItem(row, col_num);
			collision_array[row_num * width + col_num] = (int)PyLong_AsLong(value);
		};
	};
	
	struct Vector2 start_position = {x, y};
	int length = abs((stop - start) / step);
	PyObject *py_list = PyList_New(length);
	
	double angle = start;
	for (int i = 0; i < length; i++) {
		PyObject *point = PyList_New(2);
		struct Vector2 end_point = from_angle(angle, start_position, max_distance, width, height, collision_array, tile_size);
		PyList_SetItem(point, 0, PyLong_FromLong(round(end_point.x)));
		PyList_SetItem(point, 1, PyLong_FromLong(round(end_point.y)));
		angle += step;
		PyList_SetItem(py_list, i, PyList_AsTuple(point));
		Py_DECREF(point);
	};
	
	free(collision_array);

	return py_list;
}


static PyMethodDef DDAMethods[] = {
    {"from_angle", method_from_angle, METH_VARARGS, 
	"Calculate intersection using DDA and a tiled world's array from angle and starting position."},
	
	{"from_angle_range", method_from_angle_range, METH_VARARGS, 
	"Calculate intersection using DDA and a tiled world's array from a range of angles and a starting position."},
	
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef ddamodule = {
    PyModuleDef_HEAD_INIT,
    "dda",
    "Library for DDA algorithm related functions.",
    -1,
    DDAMethods
};


PyMODINIT_FUNC PyInit_dda(void) {
    return PyModule_Create(&ddamodule);
}


int main() {
	int map[4][4] = {
		{0, 0, 1, 1},
		{0, 0, 0, 1},
		{0, 0, 0, 1},
		{0, 0, 0, 1},
	};
	
	struct Vector2 position = {16, 48};
	struct Vector2 value = from_angle(3.14 / 4, position, 185, 4, 4, *map, 16);
	printf("%f %f", value.x, value.y);
	
	return 0;
}
