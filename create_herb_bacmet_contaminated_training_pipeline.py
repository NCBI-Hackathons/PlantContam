import pandas as pd
from itertools import groupby
import string
from sequence_mixing import *


"""Read in the ~230 herbicide resistant sequences
and the ~150,000 metal resistant sequences"""
herbs = pd.read_pickle('herb_seqs.p')
bacmets = pd.read_pickle('bacmet_seqs.p')

herb_contamination_count = 10000
bacmet_contamination_count = 30000

"""Read in the training/validation data"""
files = ['RefSeq/Arabidopsis_thaliana/GCF_000001735.3_TAIR10_genomic.fna',
        'RefSeq/Medicago_truncatula/GCF_000219495.3_MedtrA17_4.0_genomic.fna',
        'RefSeq/Physcomitrella_patens/GCF_000002425.3_V1.1_genomic.fna',
        'RefSeq/Selaginella_moellendorffii/GCF_000143415.3_v1.0_genomic.fna',
        'RefSeq/Brachypodium_distachyon/GCF_000005505.2_Brachypodium_distachyon_v2.0_genomic.fna',
        'RefSeq/Nicotiana_sylvestris/GCF_000393655.1_Nsyl_genomic.fna']

species = ['Arabidopsis_thaliana', 'Medicago_truncatul', 'Physcomitrella_patens',
            'Selaginella_moellendorffii', 'Brachypodium_distachyon', 'Nicotiana_sylvestris']

data_points = {}
first_column = ['Herbicide Resistant Contamination']*herb_contamination_count \
                + ['Metal Resistance Contamination']*bacmet_contamination_count

"""Replace all non-A, C, G, T characters in a given sequence
with A, C, G, T, each possibility being equally likely"""
def clean_sequence(seq):
    good_chars = ['A', 'C', 'G', 'T']
    new_chars = []
    for i in range(len(seq)):
        if seq[i] not in good_chars:
            r = random.random()
            index = (int)(len(good_chars)*r)
            if index == 4: index = 3
            new_chars.append(good_chars[index])
        else:
            new_chars.append(seq[i])
    return ''.join(new_chars)

"""Loop through each of the species"""
for i in range(len(files)):
    print i
    filename = files[i]
    speciesname = species[i]

    """Read in the sequence for the current species, and clean by
    making all letters upper case and removing any letters that are
    not one of A, C, G, T"""
    with open(filename) as f:
        groups = groupby(f, key=lambda x: not x.startswith(">"))
        d = {}
        for k,v in groups:
            if not k:
                key, val = list(v)[0].rstrip(), "".join(map(str.rstrip,next(groups)[1],""))
                d[key] = val
    f.close()

    seq_fragments = [d[key] for key in d.keys()]
    seq = ''.join(seq_fragments)
    seq = seq.upper()
    seq = seq.strip()

    good_chars = ['A', 'C', 'G', 'T']
    seq = seq.replace('N', '')

    """Contaminate the sequences by randomly inserting herbicide and
    metal resistant subsequences"""
    contaminated_seqs = []
    for j in range(herb_contamination_count):
        herb_seq = herbs[random.randint(0, len(herbs)-1)]
        contaminated_seq = random_mixed_sequence(seq, herb_seq, 400, 1200, 2000)
        contaminated_seq = clean_sequence(contaminated_seq)
        contaminated_seqs.append(contaminated_seq)

    for j in range(bacmet_contamination_count):
        bacmet_seq = bacmets[random.randint(0, len(bacmets)-1)]
        contaminated_seq = random_mixed_sequence(seq, bacmet_seq, 400, 1200, 2000)
        contaminated_seq = clean_sequence(contaminated_seq)
        contaminated_seqs.append(contaminated_seq)

    data_points[speciesname] = contaminated_seqs

"""Write everything out to a file"""
contaminated_seqs_df = pd.DataFrame(data_points, index = first_column)
contaminated_seqs_df.to_csv('herb_bacmet_contaminated_sequences_2000.csv')
