from PIL import Image
import numpy as np
import math
import cv2
import copy
from scipy.fftpack import dct, idct

class JPEGEncoder:
    def __init__(self):
        pass

    def encode(self, image_path, save_path, name):
        img = Image.open(image_path)
        print("1/10")
        # Convert image to RGB (if not already)
        img = img.convert('RGB')

        # Convert the image to a NumPy array
        img_array = np.array(img)

        # Extract R, G, B channels
        r, g, b = img_array[:,:,0], img_array[:,:,1], img_array[:,:,2]

        #plt.imshow(img)
        #plt.axis('off')
        # Create the plot with 3 subplots for R, G, B
        #fig, axs = plt.subplots(1, 3, figsize=(15, 5))

        dimy = len(r)
        dimx = len(r[0])

        # Plot Red channel
      
        # Show the plots
       #plt.tight_layout()
        #plt.show()
        print("2/10")
        for i in range(dimy):
            for j in range(dimx):
                rval = img_array[i,j,0]
                gval = img_array[i,j,1]
                bval = img_array[i,j,2]
                
                img_array[i,j,0] = round(16 + 65.481 * rval / 255 + 128.553 * gval / 255 + 24.966 * bval / 255) # Y
                img_array[i,j,1] = round(128 - 37.797 * rval / 255 - 74.203 * gval / 255 + 112.0 * bval / 255)  # Cb
                img_array[i,j,2] = round(128 + 112.0 * rval / 255 - 93.786 * gval / 255 - 18.214 * bval / 255)  # Cr

        blocks = [[[r[i*8:i*8+8,j*8:j*8+8],g[i*8:i*8+8,j*8:j*8+8],b[i*8:i*8+8,j*8:j*8+8]] for j in range(math.ceil(dimx/8))] for i in range(math.ceil(dimy/8))]
                #print(blocks[4][2][0])

        print("2.5/10")
        # for every block
        for a, row in enumerate(blocks):
            for b, block in enumerate(row):
                # for each pixel use the following formulas:
                
                for i in range(8):
                    for j in range(8):
                        try:
                            rval = block[0][i,j]
                            gval = block[1][i,j]
                            bval = block[2][i,j]
                        except:
                            # we need to expand the block basically to be 8 by 8.
                            newzero = np.zeros((8,8))
                            newone = np.zeros((8,8))
                            newtwo = np.zeros((8,8))
                            newzero[:block[0].shape[0], :block[0].shape[1]] = block[0]
                            newone[:block[1].shape[0], :block[1].shape[1]] = block[1]
                            newtwo[:block[2].shape[0], :block[2].shape[1]] = block[2]
                            block[0] = newzero
                            block[1] = newone
                            block[2] = newtwo

                            rval = block[0][i,j]
                            gval = block[1][i,j]
                            bval = block[2][i,j]

        #fig, axs = plt.subplots(1, 1, figsize=(15, 5))
        #(np.array(blocks[4][2][0]), cmap='gray', vmin = 0, vmax = 255)
        print("3/10")
        chroma_size = 2 # given blocks of 8, it would make sense to down sample it by either 1 (no change), 2, 4, or 8 (literally just 1 color per block).
        compressed_blocks = [[[np.zeros((8,8)),np.zeros((int(8/chroma_size), int(8/chroma_size))),np.zeros((int(8/chroma_size), int(8/chroma_size)))] 
                            for i in range(math.ceil(dimx/8))] for j in range(math.ceil(dimy/8))]
        # i would like to make both a downsampled form, which can basically represent the compression done thus far, as well as an 8 by 8 upscale which can easily be fed into DCT
        for a, row in enumerate(blocks):
            for b, block in enumerate(row):
                for i in range(8):
                    for j in range(8):
                        bmaxwidth = len(block[0][0])
                        bmaxheight = len(block[0])
                        compressed_blocks[a][b][0][i,j] = block[0][min(i, bmaxheight - 1),min(j, bmaxwidth - 1)]
                
                for i in range(int(8 / chroma_size)):
                    for j in range(int(8 / chroma_size)):
                        compressed_blocks[a][b][1][i,j] = np.round(np.mean(block[1][i * chroma_size:(i + 1) * chroma_size, j * chroma_size: (j+1) * chroma_size]))
                        compressed_blocks[a][b][2][i,j] = np.round(np.mean(block[2][i * chroma_size:(i + 1) * chroma_size, j * chroma_size: (j+1) * chroma_size]))

        print(f"subsampling window: {chroma_size}")
        #print(blocks[4][2][0])
        #print()
        #print(compressed_blocks[4][2][0])


        for a, row in enumerate(blocks):
            for b, block in enumerate(row):
                for i in range(8):
                    for j in range(8):
                        bmaxwidth = len(block[0][0])
                        bmaxheight = len(block[0])

                        block[0][min(i, bmaxheight - 1),min(j, bmaxwidth - 1)] = compressed_blocks[a][b][0][i,j]
                        block[1][min(i, bmaxheight - 1),min(j, bmaxwidth - 1)] = compressed_blocks[a][b][1][int(i / chroma_size),int(j / chroma_size)]
                        block[2][min(i, bmaxheight - 1),min(j, bmaxwidth - 1)] = compressed_blocks[a][b][2][int(i / chroma_size),int(j / chroma_size)]
        print("4/10")
        N = 8
        dctlist = [0,0,0,0,0,0,0,0]
        p = [96, 85, 87, 151, 176, 174, 168, 140]
        def alph(x):
            if x == 0:
                return (1. / N) ** 0.5
            else:
                return (2. / N) ** 0.5

        # calculate the dct for each position
        for i in range(8):
            sum = 0. # track the sum.
            for j in range(8):
                sum += p[j] * math.cos(math.pi * (2 * j + 1) * i / (2 * N))
            dctlist[i] = alph(i) * sum
        
        print("5/10")
        np.set_printoptions(suppress=True, precision=2)

        #print(blocks[4][2][2])

        dct_blocks = [[[np.zeros((8,8)),np.zeros((8,8)),np.zeros((8,8))] for i in range(math.ceil(dimx/8))] for j in range(math.ceil(dimy/8))]
        for a, row in enumerate(dct_blocks):
            for b, dct_block in enumerate(row):
                dct_block[0] = dct(dct(blocks[a][b][0], axis=0, norm='ortho'), axis=1, norm='ortho')
                dct_block[1] = dct(dct(blocks[a][b][1], axis=0, norm='ortho'), axis=1, norm='ortho')
                dct_block[2] = dct(dct(blocks[a][b][2], axis=0, norm='ortho'), axis=1, norm='ortho')

        # Apply DCT to the rows first, then to the columns (2D DCT)

        #print(dct_blocks[4][2][2])

        #apply quantization.
        q1 = [
            [3,2,2,3,5,8,10,12],
            [2,2,3,4,5,12,12,11],
            [3,3,3,5,8,11,14,11],
            [3,3,4,6,10,17,16,12],
            [4,4,7,11,14,22,21,15],
            [5,7,11,13,16,21,23,18],
            [10,13,16,17,21,24,24,20],
            [14,18,19,20,22,20,21,20],
            ]

        q2 = [
            [1,1,1,1,2,2,3,3],
            [1,1,1,1,2,2,2,3],
            [1,1,1,1,2,3,4,5],
            [1,1,1,2,3,4,5,7],
            [2,2,2,3,4,5,7,8],
            [2,2,3,4,5,7,8,8],
            [2,2,4,5,7,8,8,8],
            [3,3,5,7,8,8,8,8],
            ]

        for a, row in enumerate(dct_blocks):
            for b, dct_block in enumerate(row):
                for c, layer in enumerate(dct_block):
                    for d, row2 in enumerate(layer):
                        for e, cell in enumerate(row2):
                            dct_blocks[a][b][c][d][e] /= q1[d][e]
                            dct_blocks[a][b][c][d][e] = round(dct_blocks[a][b][c][d][e])
        print("6/10")
        #print(dct_blocks[4][2][2])
        data_blocks = copy.deepcopy(dct_blocks)

        for a, row in enumerate(dct_blocks):
            for b, dct_block in enumerate(row):
                for c, layer in enumerate(dct_block):
                    for d, row2 in enumerate(layer):
                        for e, cell in enumerate(row2):
                            
                            dct_blocks[a][b][c][d][e] *= q1[d][e]

        #print(dct_blocks[4][2][2])
        print("7/10")
        def countBytes(block, printvals = False):
            zigzag_indices = [
                (0, 0), (0, 1), (1, 0), (2, 0), (1, 1), (0, 2), (0, 3), (1, 2),
                (2, 1), (3, 0), (4, 0), (3, 1), (2, 2), (1, 3), (0, 4), (0, 5),
                (1, 4), (2, 3), (3, 2), (4, 1), (5, 0), (6, 0), (5, 1), (4, 2),
                (3, 3), (2, 4), (1, 5), (0, 6), (0, 7), (1, 6), (2, 5), (3, 4),
                (4, 3), (5, 2), (6, 1), (7, 0), (7, 1), (6, 2), (5, 3), (4, 4),
                (3, 5), (2, 6), (1, 7), (2, 7), (3, 6), (4, 5), (5, 4), (6, 3),
                (7, 2), (7, 3), (6, 4), (5, 5), (4, 6), (3, 7), (4, 7), (5, 6),
                (6, 5), (7, 4), (7, 5), (6, 6), (5, 7), (6, 7), (7, 6), (7, 7)
            ]

            blck = np.zeros((8,8))
            for i, row in enumerate(block):
                for j, item in enumerate(row):
                    blck[i,j] = item
            block = blck

            result = []
            for r, c in zigzag_indices:
                result.append(round(block[r][c]))
            
            rleresult = []
            zerolen = 0
            for i, val in enumerate(result):
                if val != 0 and zerolen != 0:
                    rleresult.append([0,zerolen])
                    if val < -128 and i >= 1:
                        rleresult.append(-128)
                    elif val > 126 and i >= 1:
                        rleresult.append(126)
                    else:
                        rleresult.append(val)
                    
                    zerolen = 0
                elif val != 0:
                    if val < -128 and i >= 1:
                        rleresult.append(-128)
                    elif val > 126 and i >= 1:
                        rleresult.append(126)
                    else:
                        rleresult.append(val)
                else:
                    zerolen += 1
            if zerolen != 0:
                rleresult.append([0,zerolen])
            
            datasize = 0
            for item in rleresult:
                if isinstance(item, list):
                    datasize += 2
                else:
                    datasize += 1
            datasize += 1
            if printvals:
                print(result)
                print(rleresult)
                print(datasize)
            return rleresult, datasize

        allcodes = [[[None, None, None] for i in range(math.ceil(dimx/8))] for j in range(math.ceil(dimy/8))]
        print("8/10")
        totalbytes = 0
        numberofblocks = 0
        sizeperblock = np.zeros((math.ceil(dimy/8), math.ceil(dimx/8)))
        for a, row in enumerate(data_blocks):
            for b, data_block in enumerate(row):
                code0, size0 = countBytes(data_blocks[a][b][0])
                code1, size1 = countBytes(data_blocks[a][b][1])
                code2, size2 = countBytes(data_blocks[a][b][2])

                allcodes[a][b][0] = code0
                allcodes[a][b][1] = code1
                allcodes[a][b][2] = code2

                sizeperblock[a][b] += size0 + size1 + size2
                totalbytes += sizeperblock[a][b]
                numberofblocks += 1

        print("Number of bytes used per block:")
        print(sizeperblock)
        print()
        print("Total bytes used:")
        print(totalbytes)
        print(numberofblocks)        

        byte_arr = [int(dimy / 256), dimy % 256, int(dimx / 256), dimx % 256, int(len(allcodes) / 256), len(allcodes) % 256, int(len(allcodes[0]) / 256), len(allcodes[0]) % 256] 
        some_bytes = bytearray(byte_arr)
        print("9/10")
        # Bytearray allows modification

        # Now, each block begins with the 2 byte positive integer, and then i will add 128 to all the following raw integers
        # lets just try this with code 0 0 0 for now.

        def binarizecode(bytearr, code):
            errs = 0
            bytearr.append(int(code[0] / 256))
            bytearr.append(code[0] % 256)
            for i in range(1, len(code)):
                if isinstance(code[i], list):
                    for val in code[i]:
                        bytearr.append(val + 128)
                else:
                    try:
                        bytearr.append(code[i] + 128) # might be accidentally destroying some data but idk
                    except:
                        bytearr.append(254)
                        errs += 1
            bytearr.append(127 + 128) # this is the stop code, hopefully nothing goes too wrong.
            return errs

        problems = 0

        for row in allcodes:
            for block in row:
                for layer in block:
                    problems += binarizecode(some_bytes, layer)

        print(problems) # 78 instances of a value of a coefficient being above 128 in the rest of the image. Could be acceptable loss??? idk for sure tho but 78 out of 3 MB seems not bad and idk how noticeable it will actually be.

        # Bytearray can be cast to bytes
        immutable_bytes = bytes(some_bytes)

        # Write bytes to file
        with open(f"{save_path}/{name}.txt", "wb") as binary_file:
            binary_file.write(immutable_bytes)
        
        print("10/10")

    def decode(self, image_path, save_path, name):

        with open(image_path, "rb") as binary_file:
            data = binary_file.read()

        print("1/8")

        # the dimx and dimy should be derived from the file.
        alldecodes = [[[None, None, None] for i in range(data[6] * 256 + data[7])] for j in range(data[4] * 256 + data[5])]
        rows = data[6] * 256 + data[7]
        cols = data[4] * 256 + data[5]
        dimy = data[0] * 256 + data[1]
        dimx = data[2] * 256 + data[3]
        fileidx = 8
        # currently the file index is 4.
        for i, row in enumerate(alldecodes):
            for j, block in enumerate(row):
                for k, layer in enumerate(block):
                    newcode = []
                    newcode.append(data[fileidx] * 256 + data[fileidx + 1])
                    fileidx += 2

                    while (data[fileidx] != 255):
                        if (data[fileidx] != 128):
                            newcode.append(data[fileidx] - 128)
                            fileidx += 1
                        else:
                            newcode.append([0, data[fileidx + 1] - 128])
                            fileidx += 2
                    fileidx += 1
                    alldecodes[i][j][k] = newcode
        print("2/8")
        def decode(code):
            zigzag_indices = [
                (0, 0), (0, 1), (1, 0), (2, 0), (1, 1), (0, 2), (0, 3), (1, 2),
                (2, 1), (3, 0), (4, 0), (3, 1), (2, 2), (1, 3), (0, 4), (0, 5),
                (1, 4), (2, 3), (3, 2), (4, 1), (5, 0), (6, 0), (5, 1), (4, 2),
                (3, 3), (2, 4), (1, 5), (0, 6), (0, 7), (1, 6), (2, 5), (3, 4),
                (4, 3), (5, 2), (6, 1), (7, 0), (7, 1), (6, 2), (5, 3), (4, 4),
                (3, 5), (2, 6), (1, 7), (2, 7), (3, 6), (4, 5), (5, 4), (6, 3),
                (7, 2), (7, 3), (6, 4), (5, 5), (4, 6), (3, 7), (4, 7), (5, 6),
                (6, 5), (7, 4), (7, 5), (6, 6), (5, 7), (6, 7), (7, 6), (7, 7)
            ]

            output = np.zeros((8,8))
            curridx = 0
            codeidx = 0
            while curridx < 64:
                if isinstance(code[codeidx], list):
                    curridx += code[codeidx][1]
                    codeidx += 1
                    
                else:
                    output[zigzag_indices[curridx]] = code[codeidx]
                    codeidx += 1
                    curridx += 1

                    

            return output

        q1 = [
            [3,2,2,3,5,8,10,12],
            [2,2,3,4,5,12,12,11],
            [3,3,3,5,8,11,14,11],
            [3,3,4,6,10,17,16,12],
            [4,4,7,11,14,22,21,15],
            [5,7,11,13,16,21,23,18],
            [10,13,16,17,21,24,24,20],
            [14,18,19,20,22,20,21,20],
            ]

        reconstructed_blocks = [[[np.zeros((8,8)),np.zeros((8,8)),np.zeros((8,8))] for i in range(rows)] for j in range(cols)]
        for a, row in enumerate(reconstructed_blocks):
            for b, block in enumerate(row):
                reconstructed_blocks[a][b][0] = decode(alldecodes[a][b][0])
                reconstructed_blocks[a][b][1] = decode(alldecodes[a][b][1])
                reconstructed_blocks[a][b][2] = decode(alldecodes[a][b][2])

        print("3/8")

        for a, row in enumerate(reconstructed_blocks):
            for b, dct_block in enumerate(row):
                for c, layer in enumerate(dct_block):
                    for d, row2 in enumerate(layer):
                        for e, cell in enumerate(row2):
                            
                            reconstructed_blocks[a][b][c][d][e] *= q1[d][e]

        print("4/8")
        for a, row in enumerate(reconstructed_blocks):
            for b, reconstructed_block in enumerate(row):
                reconstructed_block[0] = idct(idct(reconstructed_blocks[a][b][0], axis=0, norm='ortho'), axis=1, norm='ortho')
                reconstructed_block[1] = idct(idct(reconstructed_blocks[a][b][1], axis=0, norm='ortho'), axis=1, norm='ortho')
                reconstructed_block[2] = idct(idct(reconstructed_blocks[a][b][2], axis=0, norm='ortho'), axis=1, norm='ortho')

                for c, layer in enumerate(dct_block):
                    for d, row2 in enumerate(layer):
                        for e, cell in enumerate(row2):
                            reconstructed_block[c][d][e] = int(reconstructed_block[c][d][e])
                            
        print("5/8")

        for a, row in enumerate(reconstructed_blocks):
            for b, block in enumerate(row):
                reconstructed_blocks[a][b][0] = cv2.convertScaleAbs(reconstructed_blocks[a][b][0])
                reconstructed_blocks[a][b][1] = cv2.convertScaleAbs(reconstructed_blocks[a][b][1])
                reconstructed_blocks[a][b][2] = cv2.convertScaleAbs(reconstructed_blocks[a][b][2])

                ycbcrimage = np.stack((reconstructed_blocks[a][b][0],reconstructed_blocks[a][b][2],reconstructed_blocks[a][b][1]), axis = -1)
                rgb_image = cv2.cvtColor(ycbcrimage, cv2.COLOR_YCrCb2RGB)# kinda cheating this time but whatever
                reconstructed_blocks[a][b][0] = rgb_image[:,:,0]
                reconstructed_blocks[a][b][1] = rgb_image[:,:,1]
                reconstructed_blocks[a][b][2] = rgb_image[:,:,2]
        print("6/8")
        newimg = np.zeros((dimy, dimx, 3))

        print(np.shape(newimg))
        print(dimy)
        print(dimx)
        for a in range(dimy):
            for b in range(dimx):
                newimg[a,b,0] = reconstructed_blocks[int(a/8)][int(b/8)][0][a%8,b%8] / 256
                newimg[a,b,1] = reconstructed_blocks[int(a/8)][int(b/8)][1][a%8,b%8] / 256
                newimg[a,b,2] = reconstructed_blocks[int(a/8)][int(b/8)][2][a%8,b%8] / 256
        print("7/8")
        print(newimg)
        newimg = (newimg * 255).clip(0, 255).astype(np.uint8)
        image = Image.fromarray(newimg)
        image.save(f'{save_path}/{name}.png')
        print("8/8")