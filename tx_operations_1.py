# Import necessary libraries
import asyncio
import time
import statistics
from chainspect.redis import RedisChainspectorConnector

# Connector for the Redis instances
connector = RedisChainspectorConnector.live()

# The address to connect to
block = 750000

small, medium, big = 0, 0, 0
# It seems to fluctuate a bit and i can't find an API call to retrieve it, so i'll hardcode the latest one
transaction_fee = 5.349
batched = []
biggest_sum = {
    "txid": "",
    "input_count": 0, 
    "input_sum": 0,
    "output_sum": 0,
    "output_count": 0
              }

start_time = time.time()

async with connector as cs:
    # List all the transactions for the block
    txs = await cs.block_height_txs(block)
    # Fetch all outputs based on txs
    tx_outputs_ids = await cs.tx_outputs_multi(txs)
    # Fetch all inputs based on txs
    tx_inputs_ids = await cs.tx_inputs_multi(txs)
    
    for i, tx in enumerate(txs):
        # Since lists are ordered and after some consistency checks on the three lists returned by calls before the for loop, i'll assume they will always return in the same order 1:1 with txs order,
        # which will also be always the same and since lenght of the three lists is also 1:1
        # I'll assume we can avoid to loop a single call to tx_outputs(tx) and tx_inputs(tx) to find out inputs/outputs ids and we can just use mass calls above and indexing, reducing computation time almost in half
        outputs = tx_outputs_ids[i]
        outputs_values = await cs.output_value_multi(outputs)
        outputs_values = [_ / 1e8 for _ in outputs_values]
    
        # Same as above
        inputs = tx_inputs_ids[i]
        inputs_values = await cs.output_value_multi(inputs)
        inputs_values = [_ / 1e8 for _ in inputs_values]

        # Find biggest sum while already iterating since we have everything we need
        len_outputs = len(outputs_values)
        if sum(inputs_values) > biggest_sum["input_sum"]:
            biggest_sum["txid"] = tx
            biggest_sum["input_count"] = len(inputs)
            biggest_sum["output_count"] = len_outputs
            biggest_sum["input_sum"] = sum(inputs_values)
            biggest_sum["output_sum"] = sum(outputs_values)

        # First 3 are an int since we don't need further processing besides knowing how many there are. I saw there are some *_count methods in API but they do are probably not needed in this case 
        # Batched is a list of tx_byte_size 
        if 1 <= len_outputs <= 5:
            small+= 1
        elif 6 <= len_outputs <= 25:
            medium+= 1