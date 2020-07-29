import os


# compare two directories (original, annotated) to find words which were obscured by Philter
def compare(not_philtered_dir, philtered_dir):

    for filename in os.listdir(not_philtered_dir): # go through each file

        with open(os.path.join(not_philtered_dir, filename)) as fh:
            foriginal = fh.read().split()
        with open(os.path.join(philtered_dir, filename)) as fh:
            fphilter = fh.read().split()

        for i in range(len(foriginal)): # check each word

            ph_word = fphilter[i]
            og_word = foriginal[i]

            if og_word != ph_word: # if a word was obscured
                with open("obscured_words_out.txt", "a") as fout:
                    s = og_word+"\n"
                    fout.write(s)


def main():
    compare('../../data/mtsamples_pathology_notes/not_philtered/', '../../data/mtsamples_pathology_notes/philtered/')


main()
