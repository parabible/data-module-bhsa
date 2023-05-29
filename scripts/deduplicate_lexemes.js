const duplicates = require('./../deduplicate-lexemes/duplicates.json')

const fieldToNormalize = 'lexeme'

// Normalize a string to NFC
const normalize = str => str.normalize("NFC")

module.exports = db => {
    const updateDupLexemeStmt = db.prepare(`
        UPDATE word_features
        SET ${fieldToNormalize} = ? 
        WHERE ${fieldToNormalize} = ?`)
    const updateGloss = db.prepare(`
            UPDATE word_features
            SET gloss = ? 
            WHERE ${fieldToNormalize} = ?`)

    duplicates.forEach(duplicate => {
        const [term, dup] = duplicate.term.split(';').map(d => d.trim())
        const normalizedTerm = normalize(term)
        const normalizedDup = normalize(dup)
        updateDupLexemeStmt.run(normalizedTerm, normalizedDup)
        updateGloss.run(duplicate.gloss, normalizedTerm)
    })
}