const codyData = require("./hebrew.json")
const denylist = new Set(require("./denylist.json"))

const terms = Object.values(codyData["terms_dict"])
const codyDuplicates = terms.filter(t => /.*;.*/.test(t.term))
const usefulCodyDuplicates = codyDuplicates.filter(t => !denylist.has(t.gloss))

const codyTerms = usefulCodyDuplicates.map(t => ({ term: t.term, gloss: t.gloss }))
const jamesTerms = require("./jamesDuplicates.json")

const dupTerms = [].concat(codyTerms, jamesTerms)

console.log(JSON.stringify(dupTerms, null, 2))
