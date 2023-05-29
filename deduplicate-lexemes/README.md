# Explanation

In the ETCBC data, there are a number of "lexemes" that are unnecessarily duplicated. An example of this is the presence of מלאכת, which is, simply, the construct form of מלאכה. These duplicates make searching produce results that are missing segments of "accurate" results.

Cody Kingham made an effort to find duplicated lexemes by hand for the sake of his [vocabulary app](https://github.com/codykingham/Mahir). Critically, this data seems to be stored in: [https://github.com/codykingham/Mahir/master/sample_vocab/hebrew.json](https://raw.githubusercontent.com/codykingham/Mahir/master/sample_vocab/hebrew.json). This is the source of `hebrew.json` in the current directory.

Some of the so called duplicates were not that helpful so I exclude them based on `denylist.json`.

I have also discovered other duplicates that weren't listed and added them to `jamesDuplicates.json`. These are imported add appended to the output but no checks are made to deduplicate the duplicates. Hopefully that won't matter...

Invoking `main.js` should extract all the instances of duplicated terms with associated glosses (for reference).


**Usage**

```
node main.js > duplicates.json
```

