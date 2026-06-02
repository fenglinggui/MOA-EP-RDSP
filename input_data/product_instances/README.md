# Product Instances

This folder contains the input product-instance data used in the formal EP-RDSP experiments.

## Files

- `product_instances.json`: complete definitions of the 15 problem instances, including screw/table coordinates, dependency relations, and metadata.
- `product_instance_summary.json`: compact summary of the 15 problem instances.
- `ik_libraries/`: candidate inverse-kinematics libraries for the 15 product instances.
- `candidate_counts_by_product.json`: candidate count statistics by product.
- `ik_library_summary.json`: summary of the generated IK libraries.
- `ik_library_validation_summary.json`: validation summary for the generated IK libraries.

The first five products are base instances. Products 6-15 are combined instances generated from the base products according to the component list in `product_instance_summary.json`.
