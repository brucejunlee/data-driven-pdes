# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Tests the DatasetMeta protocol buffer."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np

from absl.testing import absltest

from pde_superresolution_2d import equations
from pde_superresolution_2d import grids
from pde_superresolution_2d import metadata_pb2
from pde_superresolution_2d import models
from pde_superresolution_2d import velocity_fields


class MetadataTest(absltest.TestCase):

  def setUp(self):
    grid_size = 200
    self.grid = grids.Grid(grid_size, grid_size, 2 * np.pi / grid_size)
    self.v_field = velocity_fields.ConstantVelocityField.from_seed(12, 6, 100)
    self.equation = equations.FiniteDifferenceAdvectionDiffusion(
        self.v_field, diffusion_const=0.1)
    self.model = models.RollFiniteDifferenceModel()
    grid_proto = self.grid.to_proto()
    equation_proto = self.equation.to_proto()
    model_proto = self.model.to_proto()
    self.metadata = metadata_pb2.Dataset(equation=equation_proto,
                                         model=model_proto,
                                         high_resolution_grid=grid_proto)

  def test_proto_conversion(self):
    self.assertEqual(
        self.metadata.high_resolution_grid.size_x, self.grid.size_x)
    self.assertEqual(
        self.metadata.high_resolution_grid.size_y, self.grid.size_y)
    self.assertAlmostEqual(
        self.metadata.high_resolution_grid.step, self.grid.step)

  def test_proto_reconstruction(self):
    grid_from_proto = grids.grid_from_proto(self.metadata.high_resolution_grid)
    equation_from_proto = equations.equation_from_proto(self.metadata.equation)
    self.assertEqual(grid_from_proto.size_x, self.grid.size_x)
    self.assertEqual(grid_from_proto.size_y, self.grid.size_y)
    self.assertAlmostEqual(grid_from_proto.step, self.grid.step)
    np.testing.assert_allclose(
        equation_from_proto.velocity_field.get_velocity_x(0, grid_from_proto),
        self.equation.velocity_field.get_velocity_x(0, self.grid))

if __name__ == '__main__':
  absltest.main()