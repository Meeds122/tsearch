module main

import term

// TODO:
// 	- Strip punctuation from words.
// 	- Skip word if banned punctuation in it e.g. HTML chars
// 	- Method to regenerate search and swap pointers when articles is changed.
// 	  i.e. hotswap. Searches should be much more common than article changes
// 	  so putting the expensive algorithm in the article change rather than search
//    makes sense (I hope).

struct Article {
	id int
	content string
}

// When we return results, we return results for the most popular keyword first
// Then, we return results for the article with the most instances of that keyword
struct Keyword {
	word string
mut:
	hits int
	found_in map[int]int // {article_id: hits in article}
}

struct Node {
	key string
mut:
	branches map[string]Node
	keywords []Keyword
}

// recursive tree algorithm, depth first fill
fn create_branch (keyword Keyword, index int, mut node Node) {
	if keyword.word[index].ascii_str() !in node.branches{
		node.branches[keyword.word[index].ascii_str()] = Node { key: keyword.word[index].ascii_str() }
	}
	if keyword.word.len - 1 == index {
		node.branches[keyword.word[index].ascii_str()].keywords << keyword
		return
	}
	else {
		create_branch(keyword, index + 1, mut node.branches[keyword.word[index].ascii_str()])
	}
	return
}

fn create_tree (keywords []Keyword) Node {
	mut root := Node{
		key: ''
	}
	for keyword in keywords {
		create_branch(keyword, 0, mut root)
	}

	return root
}

fn (article Article) kws (mut keywords map[string]Keyword) ! {
	words := article.content.split(' ').map(it.to_lower())
	if words.len < 1 {
		return error('Insufficient content in article')
	}
	for word in words {
		if word in banned_words {
			continue
		}
		else if word in keywords {
			keywords[word].hits += 1 
			if article.id in keywords[word].found_in {
				keywords[word].found_in[article.id] += 1
			}
			else {
				keywords[word].found_in[article.id] = 1
			}
		}
		else {
			keywords[word] = Keyword{
				hits: 1
				word: word
				found_in: {article.id: 1}
			}
		}
	}
}

fn main() {
	x, _ := term.get_terminal_size()

	println('Loaded Articles:')
	articles := make_articles()
	mut keywords := map[string]Keyword{}
	
	for article in articles {
		println('${article.id}: ${article.content[0..x-6]}...')
		article.kws(mut keywords) or { panic(err) }
	}
	
	println('')
	
	println('Top keywords: ')
	mut keywords_arr := keywords.values()
	keywords_arr.sort(a.hits > b.hits)
	
	for i in 0..10 {
		println('${i+1}: ${keywords_arr[i].word} = ${keywords_arr[i].hits}')
	}

	println('Total keywords = ${keywords_arr.len}')

	tree := create_tree(keywords_arr)

	println(tree)

}
