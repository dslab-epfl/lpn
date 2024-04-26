#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <assert.h>
#include <vector>

#include "jpeg_dht.h"
#include "jpeg_bit_buffer.h"
#include "jpeg_mcu_block.h"

static jpeg_dht        m_dht;
static jpeg_bit_buffer m_bit_buffer;
static jpeg_mcu_block  m_mcu_dec(&m_bit_buffer, &m_dht);
static std::vector<int> mcu_cnt;

static uint16_t m_width;
static uint16_t m_height;

typedef enum eJpgMode
{
    JPEG_MONOCHROME,
    JPEG_YCBCR_444,
    JPEG_YCBCR_420,
    JPEG_UNSUPPORTED
} t_jpeg_mode;

static t_jpeg_mode m_mode;

static uint8_t m_dqt_table[3];

#define get_byte(_buf, _idx)  _buf[_idx++]
#define get_word(_buf, _idx)  ((_buf[_idx++] << 8) | (_buf[_idx++]))

#define dprintf
#define dprintf_blk(_name, _arr, _max) for (int __i=0;__i<_max;__i++) { dprintf("%s: %d -> %d\n", _name, __i, _arr[__i]); }

extern "C" {
    int* lpn_driver(int* size, char* filepath);
}
//-----------------------------------------------------------------------------
// DecodeImage: Decode image data section (supports 4:4:4, 4:2:0, monochrom)
//-----------------------------------------------------------------------------
static bool DecodeImage(void)
{
    int16_t dc_coeff_Y = 0;
    int16_t dc_coeff_Cb= 0;
    int16_t dc_coeff_Cr= 0;
    int32_t sample_out[64];
    int     block_out[64];
    int     y_dct_out[4*64];
    int     cb_dct_out[64];
    int     cr_dct_out[64];
    int     count = 0;
    int     loop = 0;

    int block_num = 0;
    while (!m_bit_buffer.eof())
    {
        // [Y0 Y1 Y2 Y3 Cb Cr] x N
        if (m_mode == JPEG_YCBCR_420)
        {
            // Y0
            count = m_mcu_dec.decode(DHT_TABLE_Y_DC_IDX, dc_coeff_Y, sample_out);
            mcu_cnt.push_back(count);
            // Y1
            count = m_mcu_dec.decode(DHT_TABLE_Y_DC_IDX, dc_coeff_Y, sample_out);
            mcu_cnt.push_back(count);
            // Y2
            count = m_mcu_dec.decode(DHT_TABLE_Y_DC_IDX, dc_coeff_Y, sample_out);
            mcu_cnt.push_back(count);
            // Y3
            count = m_mcu_dec.decode(DHT_TABLE_Y_DC_IDX, dc_coeff_Y, sample_out);
            mcu_cnt.push_back(count);
            // Cb
            count = m_mcu_dec.decode(DHT_TABLE_CX_DC_IDX, dc_coeff_Cb, sample_out);
            mcu_cnt.push_back(count);
            // Cr
            count = m_mcu_dec.decode(DHT_TABLE_CX_DC_IDX, dc_coeff_Cr, sample_out);
            mcu_cnt.push_back(count);
        }
    //     // [Y Cb Cr] x N
    //     else if (m_mode == JPEG_YCBCR_444)
    //     {
    //         // Y
    //         count = m_mcu_dec.decode(DHT_TABLE_Y_DC_IDX, dc_coeff_Y, sample_out);
    //         m_dqt.process_samples(m_dqt_table[0], sample_out, block_out, count);
    //         dprintf_blk("DCT-IN", block_out, 64);
    //         m_idct.process(block_out, &y_dct_out[0]);

    //         // Cb
    //         count = m_mcu_dec.decode(DHT_TABLE_CX_DC_IDX, dc_coeff_Cb, sample_out);
    //         m_dqt.process_samples(m_dqt_table[1], sample_out, block_out, count);
    //         dprintf_blk("DCT-IN", block_out, 64);
    //         m_idct.process(block_out, &cb_dct_out[0]);

    //         // Cr
    //         count = m_mcu_dec.decode(DHT_TABLE_CX_DC_IDX, dc_coeff_Cr, sample_out);
    //         m_dqt.process_samples(m_dqt_table[2], sample_out, block_out, count);
    //         dprintf_blk("DCT-IN", block_out, 64);
    //         m_idct.process(block_out, &cr_dct_out[0]);

    //         ConvertYUV2RGB(block_num++, y_dct_out, cb_dct_out, cr_dct_out);
    //     }
    //     // [Y] x N
    //     else if (m_mode == JPEG_MONOCHROME)
    //     {
    //         // Y
    //         count = m_mcu_dec.decode(DHT_TABLE_Y_DC_IDX, dc_coeff_Y, sample_out);
    //         m_dqt.process_samples(m_dqt_table[0], sample_out, block_out, count);
    //         dprintf_blk("DCT-IN", block_out, 64);
    //         m_idct.process(block_out, &y_dct_out[0]);

    //         ConvertYUV2RGB(block_num++, y_dct_out, cb_dct_out, cr_dct_out);
    //     }
    }

    return true;
}
//-----------------------------------------------------------------------------
// main:
//-----------------------------------------------------------------------------
int* lpn_driver(int* size, char* filepath)
{

    const char *src_image = filepath;

    // Load source file
    uint8_t *buf = NULL;
    int      len = 0;
    FILE *f = fopen(src_image, "rb");
    if (f)
    {
        long size;

        // Get size
        fseek(f, 0, SEEK_END);
        size = ftell(f);
        rewind(f);

        // Read file data in
        buf = (uint8_t*)malloc(size);
        assert(buf);
        len = fread(buf, 1, size, f);

        fclose(f);
    }
    else
    {
        printf("can't open src_image.jpg\n");
        return NULL;
    }

    m_mode = JPEG_UNSUPPORTED;
    
    uint8_t last_b = 0;
    bool decode_done = false;
    printf("len %d\n", len);
    for (int i=0;i<len;)
    {
        uint8_t b = buf[i++];
        //-----------------------------------------------------------------------------
        // SOI: Start of image
        //-----------------------------------------------------------------------------
        if (last_b == 0xFF && b == 0xd8);
            //printf("Section: SOI\n");
        //-----------------------------------------------------------------------------
        // SOF0: Indicates that this is a baseline DCT-based JPEG
        //-----------------------------------------------------------------------------
        else if (last_b == 0xFF && b == 0xc0)
        {
            //printf("Section: SOF0\n");
            int seg_start = i;

            // Length of the segment
            uint16_t seg_len   = get_word(buf, i);

            // Precision of the frame data
            uint8_t  precision = get_byte(buf,i);

            // Image height in pixels
            m_height = get_word(buf, i);

            // Image width in pixels
            m_width = get_word(buf, i);

            // # of components (n) in frame, 1 for monochrom, 3 for colour images
            uint8_t num_comps = get_byte(buf,i);
            assert(num_comps <= 3);

            printf(" x=%d, y=%d, components=%d\n", m_width, m_height, num_comps);
            uint8_t comp_id[3];
            uint8_t comp_sample_factor[3];
            uint8_t horiz_factor[3];
            uint8_t vert_factor[3];

            for (int x=0;x<num_comps;x++)
            {
                // First byte identifies the component
                comp_id[x] = get_byte(buf,i);
                // id: 1 = Y, 2 = Cb, 3 = Cr

                // Second byte represents sampling factor (first four MSBs represent horizonal, last four LSBs represent vertical)
                comp_sample_factor[x] = get_byte(buf,i);
                horiz_factor[x]       = comp_sample_factor[x] >> 4;
                vert_factor[x]        = comp_sample_factor[x] & 0xF;
                // Third byte represents which quantization table to use for this component
                get_byte(buf,i);
            }

            m_mode = JPEG_UNSUPPORTED;

            // Single component (Y)
            if (num_comps == 1)
            {
                printf(" Mode: Monochrome\n");
                m_mode = JPEG_MONOCHROME;
            }
            // Colour image (YCbCr)
            else if (num_comps == 3)
            {
                // YCbCr ordering expected
                if (comp_id[0] == 1 && comp_id[1] == 2 && comp_id[2] == 3)
                {
                    if (horiz_factor[0] == 1 && vert_factor[0] == 1 &&
                        horiz_factor[1] == 1 && vert_factor[1] == 1 &&
                        horiz_factor[2] == 1 && vert_factor[2] == 1)
                    {
                        m_mode = JPEG_YCBCR_444;
                        printf(" Mode: YCbCr 4:4:4\n");
                    }
                    else if (horiz_factor[0] == 2 && vert_factor[0] == 2 &&
                             horiz_factor[1] == 1 && vert_factor[1] == 1 &&
                             horiz_factor[2] == 1 && vert_factor[2] == 1)
                    {
                        m_mode = JPEG_YCBCR_420;
                        printf(" Mode: YCbCr 4:2:0\n");
                    }
                }
            }

            i = seg_start + seg_len;
        }
        //-----------------------------------------------------------------------------
        // DQT: Quantisation table
        //-----------------------------------------------------------------------------
        else if (last_b == 0xFF && b == 0xdb)
        {
            //printf("Section: DQT Table\n");
            int seg_start = i;
            uint16_t seg_len   = get_word(buf, i);
            // m_dqt.process(&buf[i], seg_len);
            i = seg_start + seg_len;
        }
        //-----------------------------------------------------------------------------
        // DHT: Huffman table
        //-----------------------------------------------------------------------------
        else if (last_b == 0xFF && b == 0xc4)
        {
            int seg_start = i;
            uint16_t seg_len   = get_word(buf, i);
            //printf("Section: DHT Table\n");
            m_dht.process(&buf[i], seg_len);
            i = seg_start + seg_len;
        }
        //-----------------------------------------------------------------------------
        // EOI: End of image
        //-----------------------------------------------------------------------------
        else if (last_b == 0xFF && b == 0xd9)
        {
            //printf("Section: EOI\n");
            break;
        }
        //-----------------------------------------------------------------------------
        // SOS: Start of Scan Segment (SOS)
        //-----------------------------------------------------------------------------
        else if (last_b == 0xFF && b == 0xda)
        {
            //printf("Section: SOS\n");
            int seg_start = i;

            if (m_mode == JPEG_UNSUPPORTED)
            {
                printf("ERROR: Unsupported JPEG mode\n");
                break;
            }

            uint16_t seg_len   = get_word(buf, i);

            // Component count (n)
            uint8_t  comp_count = get_byte(buf,i);

            // Component data
            for (int x=0;x<comp_count;x++)
            {
                // First byte denotes component ID
                uint8_t comp_id = get_byte(buf,i);

                // Second byte denotes the Huffman table used (first four MSBs denote Huffman table for DC, and last four LSBs denote Huffman table for AC)
                uint8_t comp_table = get_byte(buf,i);

                printf(" %d: ID=%x Table=%x\n", x, comp_id, comp_table);
            }

            // Skip bytes
            get_byte(buf,i);
            get_byte(buf,i);
            get_byte(buf,i);

            i = seg_start + seg_len;

            //-----------------------------------------------------------------------
            // Process data segment
            //-----------------------------------------------------------------------
            m_bit_buffer.reset(len);
            while (i < len)
            {
                b = buf[i];
                if (m_bit_buffer.push(b))
                    i++;
                // Marker detected (reverse one byte)
                else
                {
                    i--;
                    break;
                }
            }
            printf("decode img\n");
            decode_done = DecodeImage();
        }
         else if (last_b == 0xFF && b == 0xc2)
        {
            //printf("Section: SOF2\n");
            int seg_start = i;
            uint16_t seg_len   = get_word(buf, i);
            i = seg_start + seg_len;

            printf("ERROR: Progressive JPEG not supported\n");
            break; // ERROR: Not supported
        }
        else if (last_b == 0xFF && b == 0xdd)
        {
            //printf("Section: DRI\n");
            int seg_start = i;
            uint16_t seg_len   = get_word(buf, i);
            i = seg_start + seg_len;            
        }
        else if (last_b == 0xFF && b >= 0xd0 && b <= 0xd7)
        {
            //printf("Section: RST%d\n", b - 0xd0);
            int seg_start = i;
            uint16_t seg_len   = get_word(buf, i);
            i = seg_start + seg_len;
        }
        else if (last_b == 0xFF && b >= 0xe0 && b <= 0xef)
        {
            //printf("Section: APP%d\n", b - 0xe0);
            int seg_start = i;
            uint16_t seg_len   = get_word(buf, i);
            i = seg_start + seg_len;
        }
        else if (last_b == 0xFF && b == 0xfe)
        {
            //printf("Section: COM\n");
            int seg_start = i;
            uint16_t seg_len   = get_word(buf, i);
            i = seg_start + seg_len;
        }

        last_b = b;
    }
    int sum = 0;
    *size = mcu_cnt.size();
    // printf("done with mcu_cnt size %d \n", mcu_cnt.size());
    int* arr = (int*) malloc(mcu_cnt.size()*sizeof(int));
    for (size_t i = 0; i < mcu_cnt.size(); ++i) {
        arr[i]= mcu_cnt[i];
    }
    return arr;      
}
