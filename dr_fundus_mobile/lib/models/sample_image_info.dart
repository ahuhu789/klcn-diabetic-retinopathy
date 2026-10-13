class SampleImageInfo {
  final String id;
  final String filename;
  final String name;
  final String category;
  final String? tag;
  final String badgeColor;
  final String? description;
  final String url;

  SampleImageInfo({
    required this.id,
    required this.filename,
    required this.name,
    this.category = 'Khác',
    this.tag,
    this.badgeColor = 'blue',
    this.description,
    required this.url,
  });

  factory SampleImageInfo.fromJson(Map<String, dynamic> json) {
    return SampleImageInfo(
      id: json['id'] ?? '',
      filename: json['filename'] ?? '',
      name: json['name'] ?? '',
      category: json['category'] ?? 'Khác',
      tag: json['tag'],
      badgeColor: json['badge_color'] ?? 'blue',
      description: json['description'],
      url: json['url'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'filename': filename,
      'name': name,
      'category': category,
      'tag': tag,
      'badge_color': badgeColor,
      'description': description,
      'url': url,
    };
  }
}
