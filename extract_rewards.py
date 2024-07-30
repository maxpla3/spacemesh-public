from datetime import datetime, timedelta
import sqlite3
import bech32
import argparse


genesis_date = datetime(2023, 7, 14, 10, 0)

def bech32_to_hex(bech32_string):
    """Decode a bech32 encoded string into its hex representation."""
    hrp, words = bech32.bech32_decode(bech32_string)
    data = bech32.convertbits(words, frombits=5, tobits=8, pad=False)
    return bytes(data).hex()

def layer_timestamp(layer):
    timestamp = genesis_date + timedelta(minutes=5*layer)
    return timestamp.strftime("%Y,%m,%d,%H:%M")

parser = argparse.ArgumentParser(description="""
To retrieve the rewards provide a path to a fully synced database (state.sql) and the reward coinbase.
""")

parser.add_argument(
    "--state-file",
    help="Location of state.sql.",
    default=".",
    required=True,
    action="store",
)

parser.add_argument(
    "--coinbase",
    help="Your reward coinbase, e.g. sm1qqqqqq4flhsh6f3feg5g92w54mnhj53j3ged8dgb5rbcd.",
    required=True,
    action="store",
)

args = parser.parse_args()

coinbase_hex = bech32_to_hex(args.coinbase)

conn = sqlite3.connect(args.state_file)
cursor = conn.cursor()
cursor.execute(f"SELECT layer, total_reward/1000000000.0 reward FROM rewards WHERE coinbase = X'{coinbase_hex}'")
results = cursor.fetchall()
conn.close()

total_rewards = 0
with open("rewards.csv", mode='w') as file:
    file.write("year, month, day, time, layer, reward (SMH)\n")
    for layer, reward in results:
        file.write(f"{layer_timestamp(layer)},{layer},{reward}\n")
        total_rewards += reward

print(f"Total rewards: {total_rewards} SMH")
print("Results have been written to rewards.csv.")

