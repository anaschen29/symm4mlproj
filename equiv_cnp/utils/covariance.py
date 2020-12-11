import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.utils.data as utils

import e2cnn
from e2cnn import gspaces, group


def eigenvalue_covariance_estimate_rep(gspace):
    """
    Input:
        gspace - instance of e2cnn.gspaces.r2.rot2d_on_r2.Rot2dOnR2 - underlying group

    Output:
        psd_rep - instance of e2cnn.group.Representation - group representation of the group representation before the covariance
    """
    # Change of basis matrix:
    change_of_basis = np.array([[1, 1.0, 0.0], [0.0, 0.0, 1.0], [1, -1.0, 0.0]])

    # Get group order and control:
    N = gspace.fibergroup.order()
    if N <= 3 and N != -1:
        sys.exit("Group order is not valid.")

    if isinstance(gspace, gspaces.FlipRot2dOnR2):
        irreps = (
            ["irrep_0,0", "irrep_1,2"]
            if N > 4
            else ["irrep_0,0", "irrep_1,2", "irrep_1,2"]
        )
    elif isinstance(gspace, gspaces.Rot2dOnR2):
        irreps = ["irrep_0", "irrep_2"] if N > 4 else ["irrep_0", "irrep_2", "irrep_2"]
    else:
        sys.exit("Error: Unknown group.")

    psd_rep = e2cnn.group.Representation(
        group=gspace.fibergroup,
        name="eig_val_rep",
        irreps=irreps,
        change_of_basis=change_of_basis,
        supported_nonlinearities=["n_relu"],
    )

    return psd_rep


def get_pre_covariance_rep(gspace, covariance_activation="quadratic"):
    if covariance_activation == "quadratic":
        if isinstance(gspace, gspaces.FlipRot2dOnR2):
            vec_rep = gspace.irrep(1, 1)
        else:
            vec_rep = gspace.irrep(1)
        return group.directsum(2 * [vec_rep])
    elif covariance_activation == "eigenvalue":
        return eigenvalue_covariance_estimate_rep(gspace)
    else:
        raise ValueError(
            f"{covariance_activation} is not a recognised covariance activation type"
        )


def get_pre_covariance_dim(covariance_activation="quadratic"):
    if covariance_activation == "quadratic":
        return 4
    elif covariance_activation == "eigenvalue":
        return 6
    elif covariance_activation == "diagonal":
        return 2
    else:
        raise ValueError(
            f"{covariance_activation} is not a recognised covariance activation type"
        )