# Import necessary libraries
import asyncio
import time
from collections.abc import Sequence
from chainspect.redis import RedisChainspectorConnector

CONCURRENT_WORKERS = 30

async def get_forward_tree_address_from_block(cs, address_to_reach, block, max_distance=3) -> list[str]:
    """
    Returns a list of addresses of the initial outputs that can reach a specific address within the y-hop limit.
    
    Parameters
    ----------
    cs : Chainspector
        An instance of a `Chainspector`.
    address_to_reach : str
        Address to be used as the end of the path.
    block : int
        Block number
    max_distance : int
        Limits the distance to search. If no path within `max_distance` from
        the list of inputs in the 'block' to `address_to_reach`, the result will be an empty list.
    
    Returns
    -------
    list[str]
        A list of all addresses that have a path between 'address_to_reach' and 
        all the addresses in the selected 'block'.
    """
    class StepsExceeded(Exception):
        pass

    class MissingNextTx(Exception):
        pass
        
    async def next_step(queue: asyncio.Queue, cs: RedisChainspectorConnector) -> None:
        while True:
            try:
                if queue.empty():
                    break
                    
                output_to_process, i, og_output_address= await queue.get()
                if i >= max_distance:
                    raise StepsExceeded("Steps Exceeded")

                next_tx = await cs.output_next_tx(output_to_process)
                if not next_tx:
                    raise MissingNextTx("Missing Next Tx")
    
                next_tx_outputs = await cs.tx_outputs(next_tx[0])
                #output_address = await cs.output_address(output_to_process)
    
                for next_tx_output in next_tx_outputs:
                    next_tx_address = await cs.output_address(next_tx_output)
                    if next_tx_address== address_to_reach:
                        list_of_addresses.append(og_output_address)
                        break
                    else:
                        queue.put_nowait((next_tx_output, i+1, og_output_address))
                        
            except Exception as e:
                queue.task_done()
                continue
                
                        
    queue = asyncio.Queue()
    # List all the transactions for the block
    txs = await cs.block_height_txs(block)
    # Fetch all outputs based on txs
    tx_outputs = await cs.tx_outputs_multi(txs)
    flattened_outputs = [output for outputs in tx_outputs for output in outputs]
    og_output_addresses = await cs.output_address_multi(flattened_outputs)
    for i, og_output in enumerate(flattened_outputs):
        queue.put_nowait((og_output, 0, og_output_addresses[i]))

    tasks, list_of_addresses = [], []
    for _ in range(CONCURRENT_WORKERS):
        tasks.append(next_step(queue, cs)
    
    await asyncio.gather(*tasks)
  
    return list_of_addresses


async def test_get_forward_tree_address(cs: RedisChainspectorConnector):
    """
    Test function to verify that get_forward_tree_address works correctly.
    """
    # Test 1
    address_to_connect = '18mddZvpUTLqb1twgokF5HtVbb45YJFhdB'
    expected_addresses = ['1HfrzKE9K8cHQ1Le6SgARp8uoba5gruAx9', '1BvccStvq5piUqd7AByST9sqWWfpHjz3Et']
    block = 120001
    max_distance = 2
    result = await get_forward_tree_address_from_block(cs, address_to_connect, block, max_distance)
    assert set(result) == set(expected_addresses), f"Expected {expected_addresses}, but got {result}"
    print("Test 1 successful !")
    
    # Test 2
    address_to_connect = '1CDysWzQ5Z4hMLhsj4AKAEFwrgXRC8DqRN'
    expected_addresses = ['18eGJJUZeKoCHb7CXQdhJhQrKPhHUsVbfE', '1MtWU6RkJbXJkFv6Dw37Q7ukekQAXMjeQe',
                          '1PQjzVgHnz7T6Lr8zgRLop8K5qcL5xQMfz', '1Tp3NNN7c3xMaQuew87ecpZ4S3bnLaesX',
                          '1PCZT941y7t12BMWeQYTuSZL5XC5235e6a']
    block = 160004
    max_distance = 3
    result = await get_forward_tree_address_from_block(cs, address_to_connect, block, max_distance)
    assert set(result) == set(expected_addresses), f"Expected {expected_addresses}, but got {result}"
    print("Test 2 successful !")

if __name__ == "__main__":
    connector = RedisChainspectorConnector.live()
    async with connector as cs:
        start_time = time.time()
        await test_get_forward_tree_address(cs)
        print(f'\ncomputation time: {time.time() - start_time:.3f} seconds')