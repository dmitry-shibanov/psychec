// Copyright (c) 2008 Roberto Raggi <roberto.raggi@gmail.com>
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.

#ifndef PSYCHE_MEMORY_POOL_H__
#define PSYCHE_MEMORY_POOL_H__

#include "FrontendConfig.h"

#include <cstddef>
#include <new>

namespace psyche {

class MemoryPool;

class CFE_API MemoryPool
{
    MemoryPool(const MemoryPool &other);
    void operator =(const MemoryPool &other);

public:
    MemoryPool();
    ~MemoryPool();

    void reset();

    inline void *allocate(size_t size)
    {
        size = (size + 7) & ~7;
        if (_ptr && (_ptr + size < _end)) {
            void *addr = _ptr;
            _ptr += size;
            return addr;
        }
        return allocate_helper(size);
    }

private:
    void *allocate_helper(size_t size);

private:
    char **_blocks;
    int _allocatedBlocks;
    int _blockCount;
    char *_ptr;
    char *_end;

    enum
    {
        BLOCK_SIZE = 8 * 1024,
        DEFAULT_BLOCK_COUNT = 8
    };
};

class CFE_API Managed
{
    Managed(const Managed &other);
    void operator = (const Managed &other);

public:
    Managed();
    virtual ~Managed();

    void *operator new(size_t size, MemoryPool *pool);
    void operator delete(void *);
    void operator delete(void *, MemoryPool *);
};

} // namespace psyche

#endif
