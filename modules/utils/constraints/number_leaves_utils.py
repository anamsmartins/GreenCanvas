from .shape_ratio_utils import shape_ratio

def compute_number_of_leaves(branch_offset, parent_branch_length, quality=1):
    ratio = branch_offset / parent_branch_length
    return int(20 * shape_ratio(ratio) * quality)