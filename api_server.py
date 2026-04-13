from flask import Flask, jsonify, request

app = Flask(__name__)

# 模拟数据库
posts = {
    1: {"id": 1, "title": "Post 1", "body": "Content 1"},
    2: {"id": 2, "title": "Post 2", "body": "Content 2"},
    3: {"id": 3, "title": "Post 3", "body": "Content 3"},
}

@app.route('/posts', methods=['GET'])
def get_posts():
    """GET /posts - 获取所有帖子"""
    return jsonify(list(posts.values()))

@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """GET /posts/1 - 获取单个帖子"""
    if post_id in posts:
        return jsonify(posts[post_id])
    return jsonify({"error": "Not found"}), 404

@app.route('/posts', methods=['POST'])
def create_post():
    """POST /posts - 创建新帖子"""
    data = request.get_json()
    new_id = max(posts.keys()) + 1
    posts[new_id] = {
        "id": new_id,
        "title": data.get("title", ""),
        "body": data.get("body", "")
    }
    return jsonify(posts[new_id]), 201

if __name__ == '__main__':
    print("=" * 50)
    print("API Server 运行在: http://localhost:8080")
    print("支持的接口:")
    print("  GET    /posts           - 获取所有帖子")
    print("  GET    /posts/1         - 获取帖子1")
    print("  POST   /posts           - 创建帖子")
    print("=" * 50)
    app.run(port=8080, debug=True)