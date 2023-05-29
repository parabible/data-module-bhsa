const { transliterate } = require("hebrew-transliteration")
const INSERT_LIMIT = 5000

const generateBulkInsertSql = values =>
    `WITH updated(wid, transliteration) AS (VALUES
        ${values.map(({ wid, transliteration }) => `(${wid}, '${transliteration}')`).join(",")}
    )
    UPDATE word_features
        SET 
        transliteration = updated.transliteration
    FROM updated
    WHERE (word_features.wid = updated.wid)`

module.exports = db => {
    // Check if column exists on table in sqlite using better-sqlite3
    const checkColumnExists = (table, column) => {
        const sql = `PRAGMA table_info(${table})`
        const columns = db.prepare(sql).all()
        return columns.find(c => c.name === column)
    }
    if (!checkColumnExists('word_features', 'transliteration')) {
        console.log('Adding transliteration column to word_features')
        // Add column to word_features table
        db.prepare(`ALTER TABLE word_features ADD COLUMN transliteration TEXT`).run()
    }

    // Loop through all words in word_features table and add transliteration
    const sql = `SELECT wid as id, lexeme FROM word_features`
    const words = db.prepare(sql).all().filter(({ lexeme }) => lexeme)
    // const stmt = db.prepare(`UPDATE word_features SET transliteration = ? WHERE wid = ?`)
    // const wordsLength = words.length
    let counter = 0
    while (words.length > 0) {
        const values = words
            .splice(0, INSERT_LIMIT)
            .map(({ id, lexeme }) => ({
                wid: id,
                transliteration: transliterate(lexeme)
            }))
        const addTransliterationSql = generateBulkInsertSql(values)
        db.prepare(addTransliterationSql).run()
        if (++counter % 10 === 0) {
            console.log(`${counter}/${words.length}`)
        }
    }
}