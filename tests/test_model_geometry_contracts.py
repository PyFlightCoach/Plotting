from math import pi

import numpy as np

from geometry import Point, Quaternion, Transformation
from plotting.model import OBJ


def test_obj_triangle_parse_scale_transform_and_plotly_mesh(tmp_path):
    triangle = tmp_path / "triangle.obj"
    triangle.write_text(
        "v 0 0 0\n"
        "v 1 0 0\n"
        "v 0 1 0\n"
        "vn 0 0 1\n"
        "f 1//1 2//1 3//1\n",
        encoding="utf-8",
    )

    with triangle.open(encoding="utf-8") as source:
        mesh_source = OBJ.from_obj_file(source)

    expected_vertices = np.array(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
    )
    expected_faces = np.array([[0, 1, 2]])
    np.testing.assert_array_equal(mesh_source.vertices.data, expected_vertices)
    np.testing.assert_array_equal(mesh_source.faces, expected_faces)
    assert mesh_source.normals == [["0", "0", "1"]]

    scaled = mesh_source.scale(2.0)
    np.testing.assert_array_equal(
        scaled.vertices.data,
        np.array([[0.0, 0.0, 0.0], [2.0, 0.0, 0.0], [0.0, 2.0, 0.0]]),
    )
    np.testing.assert_array_equal(scaled.faces, expected_faces)

    # Analytic +90 degree Z rotation followed by translation (1, 2, 3).
    transform = Transformation(
        Point(1.0, 2.0, 3.0),
        Quaternion.from_euler(Point(0.0, 0.0, pi / 2)),
    )
    transformed = scaled.transform(transform)
    expected_transformed = np.array(
        [[1.0, 2.0, 3.0], [1.0, 4.0, 3.0], [-1.0, 2.0, 3.0]]
    )
    np.testing.assert_allclose(transformed.vertices.data, expected_transformed, atol=1e-12)
    np.testing.assert_array_equal(transformed.faces, expected_faces)

    plotly_mesh = transformed.create_mesh(colour="#123456", name="unit-triangle")
    np.testing.assert_allclose(plotly_mesh.x, [1.0, 1.0, -1.0], atol=1e-12)
    np.testing.assert_allclose(plotly_mesh.y, [2.0, 4.0, 2.0], atol=1e-12)
    np.testing.assert_allclose(plotly_mesh.z, [3.0, 3.0, 3.0], atol=1e-12)
    assert list(plotly_mesh.i) == [0]
    assert list(plotly_mesh.j) == [1]
    assert list(plotly_mesh.k) == [2]
    assert plotly_mesh.color == "#123456"
    assert plotly_mesh.name == "unit-triangle"
    np.testing.assert_array_equal(mesh_source.vertices.data, expected_vertices)
    np.testing.assert_array_equal(mesh_source.faces, expected_faces)
