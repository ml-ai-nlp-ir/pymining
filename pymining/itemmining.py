from collections import defaultdict, deque, namedtuple
import sys

CountTrans = namedtuple('CountT', ['count', 'trans'])

    #def __init__(self, init_seq, key_func):
        #self.seq = [key_func(i) for i in init_seq]
        #self.current = 0

    #def transform(self, frequencies):
        #self.seq = [(frequencies[i], i) for i in self.seq]
        #self.seq.sort()


class Transaction(object):
    
    def __init__(self, seq, current_pos=0):
        self.seq = seq
        self.current_pos = current_pos

    def first_item(self):
        return self.seq[self.current_pos]

    def minus_first(self):
        self.current_pos += 1

    def __len__(self):
        return len(self.seq) - self.current_pos

    def __str__(self):
        return 'Pos: {0}\nSeq:{1}'.format(self.current_pos, self.seq)

    def __repr__(self):
        return self.__str__()


class SamInput(object):
    
    def __init__(self, tuples, current_pos=0, end_pos=None):
        self.tuples = tuples
        self.current_pos = current_pos
        if end_pos is None:
            self.end_pos = len(tuples) -1
        else:
            self.end_pos = end_pos

    def first_item(self):
        current_pos = self.current_pos
        if current_pos > self.end_pos:
            raise Exception('SamInput is empyt')
        return self.tuples[current_pos]

    def popleft(self):
        current_pos = self.current_pos
        if current_pos > self.end_pos:
            raise Exception('SamInput is empty.')
        value = self.tuples[current_pos]
        self.current_pos = current_pos + 1
        return value
    
    def append(self, value):
        new_pos = self.end_pos + 1
        if new_pos >= len(self.tuples):
            self.tuples.append(value)
        else:
            self.tuples[new_pos] = value
        self.end_pos = new_pos

    def reset(self):
        self.current_pos = -1
        self.end_pos = 0

    def __len__(self):
        size = self.end_pos - self.current_pos + 1
        return size

    def __str__(self):
        return 'Pos: {0}, End: {1}\nTuples:{2}'.format(self.current_pos,
                self.end_pos, self.tuples)

    def __repr__(self):
        return self.__str__()

    def copy(self):
        # Copy the tuples, but not the underlying sequence
        tuples = [
                CountTrans(ct.count, 
                Transaction(ct.trans.seq, ct.trans.current_pos))
                for ct in self.tuples]
        return SamInput(tuples, self.current_pos, self.end_pos)


def compare(t1, t2):
    '''Returns r < 1 if t1 < t2, r > 1 if t2 > t1, and r == 0 if t1 == t2'''
    c1= t1.current_pos
    c2 = t2.current_pos
    s1 = len(t1)
    s2 = len(t2)
    while c1 < s1 and c2 < s2:
        v1 = t1.seq[c1]
        v2 = t2.seq[c2]
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
        c1 += 1
        c2 += 1

    return s1 - s2


def get_frequencies(transactions):
    frequencies = defaultdict(int)
    for transaction in transactions:
        for item in transaction:
            frequencies[item] += 1
    return frequencies


def get_sam_input(sequences, key_func):
    key_seqs = [[key_func(i) for i in sequence] for sequence in sequences]

    # Get frequencies of individual keys
    frequencies = get_frequencies(key_seqs)

    asorted_seqs = []
    for key_seq in key_seqs:
        # Sort each transaction (infrequent key first)
        l = [(frequencies[i], i) for i in key_seq]
        l.sort()
        asorted_seqs.append(tuple(l))
    # Sort all transactions. Those with infrequent key first, first
    asorted_seqs.sort()

    transactions = [Transaction(seq) for seq in asorted_seqs]
    
    # Group same transactions together.
    tuples = []
    visited = {}
    current = 0
    for transaction in transactions:
        seq = transaction.seq
        if seq not in visited:
            tuples.append(CountTrans(1, transaction))
            visited[seq] = current
            current += 1
        else:
            i = visited[seq]
            (count, transaction) = tuples[i]
            tuples[i] = CountTrans(count + 1, transaction)

    sam_input = SamInput(tuples)
    return sam_input


def get_default_transactions():
    return (
            ('a', 'd'),
            ('a', 'c', 'd', 'e'),
            ('b', 'd'),
            ('b', 'c', 'd'),
            ('b', 'c'),
            ('a', 'b', 'd'),
            ('b', 'd', 'e'),
            ('b', 'c', 'd', 'e'),
            ('b', 'c'),
            ('a', 'b', 'd')
            )




def get_sorted_transactions(transactions, frequencies):
    return [
            sorted(transaction, key=lambda e: frequencies[e]) for transaction
            in transactions]


def get_asorted_transactions(transactions, frequencies):
    return sorted(transactions, key=lambda t: lexi_repr(t, frequencies))


def get_sam_data(transactions):
    sam_data = deque()
    visited = {}
    current = 0
    for transaction in transactions:
        key = str(transaction)
        if key not in visited:
            sam_data.append((1, transaction))
            visited[key] = current
            current += 1
        else:
            # This cannot be a list... sorry!
            # TODO CHANGE all internal lists for tuples... sorry
            (count, transaction) = sam_data[visited[key]]
            sam_data[visited[key]] = (count + 1, transaction)

    return sam_data


def transform(transactions):
    frequencies = get_frequencies(transactions)
    sorted_transactions = get_sorted_transactions(transactions, frequencies)
    asorted_transactions = get_asorted_transactions(sorted_transactions,
            frequencies)
    sam_data = get_sam_data(asorted_transactions)
    return (sam_data, frequencies)


def lexi_repr(transaction, frequencies):
    return [(frequencies[i], i) for i in transaction]

# ALMOST, but ad should be four
# cd is reported twice with different values
# b and d are wrong.
# again, look at the return value (debug -1)
def sam(sam_data, fis, min_support, frequencies):
    #print('Debug -1: sam_data={0}, fis={1}'.format(sam_data, fis))
    n = 0
    # Will contain everything, but some transactions will be pruned from their
    # prefix.
    a = deque(sam_data)
    while len(a) > 0 and len(a[0][1]) > 0:
        #print('DEBUG 0: a={0}'.format(a))
        # contains the prefix
        b = deque()
        s = 0
        i = a[0][1][0]
        while len(a) > 0 and len(a[0][1]) > 0 and a[0][1][0] == i:
            s = s + a[0][0]
            a[0] = (a[0][0], a[0][1][1:])
            if len(a[0][1]) > 0:
                b.append(a.popleft())
            else:
                a.popleft()
        #print('DEBUG 1: a={0}, b={1}'.format(a,b))
        # Is this a clone OR a pointer...
        # contains the prefix
        c = deque(b)
        d = deque() # could reuse a, because it erase it... but what about b...
        while len(a) > 0 and len(b) > 0:
            lexi_a = lexi_repr(a[0][1], frequencies)
            lexi_b = lexi_repr(b[0][1], frequencies)
            if lexi_a > lexi_b:
                #print('a > b a={0}, b={1}'.format(lexi_a, lexi_b))
                d.append(b.popleft())
            elif lexi_a < lexi_b:
                #print('a < b a={0}, b={1}'.format(lexi_a, lexi_b))
                d.append(a.popleft())
            else:
                #print('a == b a={0}, b={1}'.format(lexi_a, lexi_b))
                b[0] = (b[0][0] + a[0][0], b[0][1])
                d.append(b.popleft())
                a.popleft()
        #print('DEBUG 3:\n a={0}\n b={1}\n d={2}'.format(a,b,d))
        while len(a) > 0:
            d.append(a.popleft())
        while len(b) > 0:
            d.append(b.popleft())
        #print('DEBUG 4:\n a={0}\n b={1}\n c={2}\n d={3}'.format(a, b, c, d))
        a = deque(d)
        if s >= min_support:
            fis.add(i)
            print('{0} with support {1}'.format(fis, s))
            n = n + 1 + sam(c, fis, min_support, frequencies)
            fis.remove(i)
        #print('LOOPING with a={0}'.format(a))

    return n


# Fix a problem... probably by looking a sam_input you'll fix it...
def sam2(sam_input, fis, min_support):
    n = 0
    a = sam_input.copy()
    while len(a) > 0 and len(a.first_item()) > 0:
        b = SamInput([])
        s = 0
        i = a.first_item().trans.first_item()
        while len(a) > 0 and len(a.first_item()) > 0 and \
                a.first_item().trans.first_item() == i:
            s = s + a.first_item().count
            a.first_item().trans.minus_first()
            if len(a.first_item().trans) > 0:
                b.append(a.popleft())
            else:
                a.popleft()
        d = SamInput(a.tuples, 0, -1)
        c = SamInput(b.tuples, b.current_pos, b.end_pos)
        while len(a) > 0 and len(b) > 0:
            cmp_val = compare(a.first_item().trans, b.first_item().trans)
            if cmp_val > 0:
                d.append(b.popleft())
            elif cmp_val < 0:
                d.append(a.popleft())
            else:
                # Combine both!
                cell = CountTrans(a.first_item().count + b.first_item().count,
                        a.first_item().trans)
                d.append(cell)
                b.popleft()
                a.popleft()
        while len(a) > 0:
            d.append(a.popleft())
        while len(b) > 0:
            d.append(b.popleft())

        a = d
        if s >= min_support:
            fis.add(i)
            print('{0} with support {1}'.format(fis, s))
            n = n + 1 + sam2(c, fis, min_support)
            fis.remove(i)

    return n


def test_sam():
    ts = get_default_transactions()
    sam_data, frequencies = transform(ts)
    fis = set()
    return sam(sam_data, fis, 2, frequencies)


def test_sam2():
    sample = get_default_transactions()
    sam_input = get_sam_input(sample, lambda e: e)
    fis = set()
    return sam2(sam_input, fis, 2)