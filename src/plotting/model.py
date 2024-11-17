from dataclasses import dataclass
from importlib.resources import files

import numpy as np
import numpy.typing as npt
import plotly.graph_objects as go
from geometry import Point, Quaternion, Transformation


@dataclass
class OBJ:
    vertices: Point
    faces: npt.NDArray
    normals: npt.NDArray = None

    @staticmethod
    def from_obj_data(odata):
        lines = odata.splitlines()

        vertices = np.array(
            [l.split(" ")[1:] for l in lines if l[:2] == "v "], dtype=float
        )
        normals = [l.split(" ")[1:] for l in lines if l[:3] == "vn "]
        faces = (
            np.array(
                [
                    [fn.split("//")[0] for fn in l.split(" ")[1:]]
                    for l in lines
                    if l[:2] == "f "
                ],
                dtype=int,
            )
            - 1
        )

        return OBJ(Point(vertices), faces, normals)

    @staticmethod
    def from_obj_file(file):
        if isinstance(file, str):
            file = open(file, encoding="utf-8")
        obj_data = file.read()
        return OBJ.from_obj_data(obj_data)

    def transform(
        self,
        transformantion: Transformation = Transformation(
            Point(0.75, 0, 0), Quaternion.from_euler(Point(np.pi, 0, -np.pi / 2))
        ),
    ):
        return OBJ(transformantion.point(self.vertices), self.faces)

    def scale(self, scale_factor):
        return OBJ(self.vertices * scale_factor, self.faces)

    def create_mesh(self, colour="orange", name: str = ""):
        """Generate a Mesh3d of my plane transformed by the requested transformation.

        Args:
            name (str, optional): The name of the series. Defaults to ''.

        Returns:
            go.Mesh3d: a plotly Mesh3d containing the model
        """

        x, y, z = self.vertices.data[:, :3].T
        I, J, K = self.faces.T
        return go.Mesh3d(
            x=x,
            y=y,
            z=z,
            i=I,
            j=J,
            k=K,
            name=name,
            showscale=False,
            hoverinfo="name",
            color=colour,
        )  # vertexcolor=vertices[:, 3:], #the color codes must be triplets of floats  in [0,1]!!


_obj_string = (
    files("plotting.data").joinpath("ColdDraftF3APlane.obj").open("r").read()
)

obj = OBJ.from_obj_data(_obj_string).transform(
    Transformation(
        Point(0.75, 0, 0), Quaternion.from_euler(Point(np.pi, 0, -np.pi / 2))
    )
)
