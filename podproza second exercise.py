    async def next_step(output_to_process: str, i: int) -> None:
        #print(output_to_process)
        while i < max_distance:
            try:
                i+= 1
                next_tx = await cs.output_next_tx(output_to_process)
                if not next_tx:
                    break
    
                try:
                    next_tx_outputs = await cs.tx_outputs(next_tx[0])
                except ValueError:
                    break
    
                tasks = []
                for next_tx_output in next_tx_outputs:
                    try:
                        next_tx_address = await cs.output_address(next_tx_output)
                    except ValueError:
                        continue
                    if address_to_reach in next_tx_address:
                        address = await cs.output_address(og_output)
                        list_of_addresses.append(address)
                        raise ValueError
                    else:
                        await next_step(next_tx_output, i)
            except Exception as e:
                continue
    
            
            
            
            
    queue = asyncio.Queue()
    list_of_addresses = []
    # List all the transactions for the block
    txs = await cs.block_height_txs(block)
    # Fetch all outputs based on txs
    tx_outputs = await cs.tx_outputs_multi(txs)
    flattened_outputs = [output for outputs in tx_outputs for output in outputs]
    #tx_outputs_addresses = await cs.output_address_multi(flattened_outputs)
    #index = dict(zip(flattened_outputs, tx_outputs_addresses))
    
    for og_output in flattened_outputs:
        i = 0
        await next_step(og_output, i)
        
    return list_of_addresses