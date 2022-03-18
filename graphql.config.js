module.exports = {
    schema: "",
    documents: "graphql-queries/*.{graphql,js,ts,jsx,tsx}",
    extensions: {
        endpoints: {
            default: {
                url: process.env.GRAPHQL_URL
            }
        }
    }
}