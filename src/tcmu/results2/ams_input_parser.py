from tcutility import timer
from tcutility.results2 import result
import os


@timer.timer
def _get_input_blocks():
    """
    This function reads input_blocks and decomposes its content into a list of blocks and a list of non-standard blocks
    The general format is as follows:

    parentblock
    - subblock
    - - subsubblock
    - subblock !nonstandard
    parentblock
    - subblock
    - - subsubblock
    - - - subsubsubblock
    - - - subsubsubblock !nonstandard

    Each subblock has to be defined within its parent block. !nonstandard indicates that the block is a non-standard block
    These blocks are special in that they can contain multiple of the same entry
    """
    blocks = []
    nonstandard_blocks = []
    parent_blocks = []  # this list tracks the parent blocks of the current block
    with open(os.path.join(os.path.split(__file__)[0], "input_blocks")) as inpblx:
        lines = inpblx.readlines()

    for line in lines:
        line = line.strip().lower()
        # we can ignore some lines
        if line == "" or line.startswith("#"):
            continue

        # block_depth indicates how many parents the block has
        block_depth = line.count("- ")
        # we reduce the amount of parent_blocks using block_depth
        # if we move from a subsubblock to a subblock we remove the last-added block
        parent_blocks = parent_blocks[:block_depth]

        # remove the "- " substrings
        block = line.split("- ")[-1].strip().lower()
        # check if the block is non-standard. If it is, remove the !nonstandard substring
        # and add it to the nonstandard_blocks list
        if block.endswith("!nonstandard"):
            block = block.split()[0]
            nonstandard_blocks.append(parent_blocks.copy() + [block])
        # in both standard and nonstandard cases add the block to blocks list
        blocks.append(parent_blocks.copy() + [block])
        # add the current block to parent_blocks for the next line
        parent_blocks.append(block.lower())

    return blocks, nonstandard_blocks


@timer.timer
def _parse_input(inp: str, open_blocks=['ams']):
    def get_possible_blocks():
        # check which blocks are openable given the current open blocks
        # we start by considering all blocks
        possible_blocks = blocks
        # we iterate through the open blocks and check if the first element in the possible_blocks is the same.
        # this way we move down through the blocks
        for open_block in open_blocks:
            possible_blocks = [block[1:] for block in possible_blocks if len(block) > 0 and block[0].lower() == open_block.lower()]
        # we want only the first element in the possible blocks, not the tails
        possible_blocks = set([block[0] for block in possible_blocks if len(block) > 0])
        return possible_blocks

    ret = result.NestedDict()
    ret.set(*open_blocks, {})

    blocks, nonstandard_blocks = _get_input_blocks()

    for line in inp.splitlines():
        line = line.strip()

        # we remove comments from the line
        # comments can be either at the start of a line or after a real statement
        # so we have to search the line for comment starters and remove the part after it
        for comment_start in ["#", "!", "::"]:
            if comment_start in line:
                idx = line.index(comment_start)
                line = line[:idx]

        # skip empty lines
        if not line:
            continue

        # if we encounter an end statement we can close the last openblock
        if line.lower().startswith("end"):
            open_blocks.pop(-1)
            continue

        # check if we are opening a block
        # We have to store the parts of a compact block (if it is compact)
        # it will be a list of tuples of key-value pairs
        compact_parts = None
        skip = False
        # check if the current line corresponds to a possible block
        for possible_block in get_possible_blocks():
            if line.lower().startswith(possible_block.lower()):
                # a block opening can either span multiple lines or can be use with compact notation
                # compact notation will always have = signs
                if "=" in line:
                    # split the key-values using some regex magic
                    compact = line[len(possible_block) :].strip()  # remove the block name
                    compact_parts = re.findall(r"""(\S+)=['"]{0,1}([^'"\n]*)['"]{0,1}""", compact)
                else:
                    skip = True
                # add the new block to the open_blocks
                open_blocks.append(possible_block)

        if ret.get(*open_blocks) is None:
            ret.set(*open_blocks, {})
        # if we are not in a compact block we can just skip
        if skip:
            continue

        # get the ret to the correct level
        # first check if the block is nonstandard
        is_nonstandard = [block.lower() for block in open_blocks] in nonstandard_blocks

        # go to the layer one above the lowest
        sett_ = ret.get(*open_blocks[:-1]) or {}

        # at the lowest level we have to check if the block is nonstandard. If it is, we add the whole line to the settings object
        if is_nonstandard and sett_[open_blocks[-1]] is None:
            sett_[open_blocks[-1]] = []
        # then finally go to the lowest ret layer
        sett_ = sett_.get(open_blocks[-1])

        # if we are in a compact block we just add all the key-value pairs
        if compact_parts:
            for key, val in compact_parts:
                sett_[key] = val
            # compact blocks do not have end statements, so we can remove it again from the open_blocks
            open_blocks.pop(-1)
        # in a normal block we split the line and add them to the settings
        else:
            # for nonstandard blocks we add the line to the list
            if is_nonstandard:
                sett_.append(line.strip())
            # for normal blocks we split the line and set it as a key, the rest of the line is the value
            else:
                sett_[line.split()[0]] = line[len(line.split()[0]) :].strip()

    for engine_block in ["engine adf", "engine dftb", "engine band"]:
        if engine_block not in ret["ams"]:
            continue
        ret["ams"][engine_block.split()[1]] = ret["ams"][engine_block]
        del ret["ams"][engine_block]

    return ret["ams"]
