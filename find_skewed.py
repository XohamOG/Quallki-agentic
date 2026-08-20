import pandas as pd
from quallki_agentic.feature_schema import FEATURE_NAMES

# Read dataset
df = pd.read_csv("MasterDatasetProcessed_Clean.csv", nrows=10000)

# Filter to only the continuous/numeric features in FEATURE_NAMES (exclude categorical ones like port/proto)
continuous = [f for f in FEATURE_NAMES if not f.startswith(('dst_port_', 'src_port_', 'proto_', 'is_attack', 'attack_type', 'label_id'))]

# Calculate skewness for these continuous features
skewness = df[continuous].skew().sort_values(ascending=False)

print("Top 25 most skewed features:")
print(skewness.head(25))
