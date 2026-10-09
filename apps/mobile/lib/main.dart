import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

const _green = Color(0xFF173F35);
const _gold = Color(0xFFC49B50);
const _storage = FlutterSecureStorage();

final apiProvider = Provider((ref) => FamilyRootsApi());

class FamilyRootsApi {
  FamilyRootsApi()
      : dio = Dio(BaseOptions(
          baseUrl: const String.fromEnvironment('API_BASE_URL',
              defaultValue: 'http://10.0.2.2:8000'),
          connectTimeout: const Duration(seconds: 10),
          receiveTimeout: const Duration(seconds: 20),
        ));
  final Dio dio;

  Future<void> login(String email, String password) async {
    final response = await dio.post('/api/v1/auth/login',
        data: {'email': email, 'password': password});
    await _storage.write(key: 'access_token', value: response.data['access_token']);
  }

  Future<void> register(String email, String password, String displayName) async {
    final response = await dio.post('/api/v1/auth/register', data: {
      'email': email,
      'password': password,
      'display_name': displayName,
    });
    await _storage.write(key: 'access_token', value: response.data['access_token']);
  }

  Future<List<dynamic>> communities() async {
    final token = await _storage.read(key: 'access_token');
    final response = await dio.get('/api/v1/communities',
        options: Options(headers: {'Authorization': 'Bearer $token'}));
    return response.data as List<dynamic>;
  }

  Future<List<dynamic>> people(String communityId) async {
    final token = await _storage.read(key: 'access_token');
    final response = await dio.get('/api/v1/communities/$communityId/persons',
        options: Options(headers: {'Authorization': 'Bearer $token'}));
    return response.data as List<dynamic>;
  }
}

void main() => runApp(const ProviderScope(child: FamilyRootsApp()));

class FamilyRootsApp extends StatelessWidget {
  const FamilyRootsApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'FamilyRoots',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          useMaterial3: true,
          colorScheme: ColorScheme.fromSeed(
            seedColor: _green,
            brightness: Brightness.light,
            surface: const Color(0xFFFFFCF5),
          ),
          scaffoldBackgroundColor: const Color(0xFFF7F5EE),
          appBarTheme: const AppBarTheme(backgroundColor: Color(0xFFF7F5EE)),
          cardTheme: CardThemeData(
            color: Colors.white,
            elevation: 0,
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(20),
                side: const BorderSide(color: Color(0xFFEAE7DE))),
          ),
          filledButtonTheme: FilledButtonThemeData(
              style: FilledButton.styleFrom(
                  backgroundColor: _green,
                  foregroundColor: Colors.white,
                  minimumSize: const Size.fromHeight(52))),
        ),
        home: const LoginScreen(),
      );
}

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});
  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _email = TextEditingController();
  final _password = TextEditingController();
  final _displayName = TextEditingController();
  bool _busy = false;
  bool _registering = false;
  String? _error;

  Future<void> _login() async {
    setState(() { _busy = true; _error = null; });
    try {
      if (_registering) {
        await ref.read(apiProvider).register(
            _email.text.trim(), _password.text, _displayName.text.trim());
      } else {
        await ref.read(apiProvider).login(_email.text.trim(), _password.text);
      }
      if (mounted) Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const CommunityScreen()));
    } on DioException catch (e) {
      setState(() => _error = e.response?.statusCode == 401
          ? 'Check your email and password.'
          : 'Could not connect to FamilyRoots. Check your connection and try again.');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        body: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(28),
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 440),
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  const Icon(Icons.account_tree_rounded, color: _green, size: 48),
                  const SizedBox(height: 26),
                  Text(_registering ? 'Start your family story' : 'Welcome home', style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.w700, color: _green)),
                  const SizedBox(height: 8),
                  Text(_registering ? 'Create an account to bring your family together.' : 'Bring your family story together.', style: Theme.of(context).textTheme.bodyLarge?.copyWith(color: Colors.black54)),
                  const SizedBox(height: 34),
                  if (_registering) ...[
                    TextField(controller: _displayName, textCapitalization: TextCapitalization.words, autofillHints: const [AutofillHints.name], decoration: const InputDecoration(labelText: 'Your name', prefixIcon: Icon(Icons.person_outline), border: OutlineInputBorder())),
                    const SizedBox(height: 16),
                  ],
                  TextField(controller: _email, keyboardType: TextInputType.emailAddress, autofillHints: const [AutofillHints.email], decoration: const InputDecoration(labelText: 'Email', prefixIcon: Icon(Icons.mail_outline), border: OutlineInputBorder())),
                  const SizedBox(height: 16),
                  TextField(controller: _password, obscureText: true, autofillHints: const [AutofillHints.password], onSubmitted: (_) => _login(), decoration: const InputDecoration(labelText: 'Password', prefixIcon: Icon(Icons.lock_outline), border: OutlineInputBorder())),
                  if (_error != null) ...[const SizedBox(height: 12), Text(_error!, style: const TextStyle(color: Colors.red))],
                  const SizedBox(height: 24),
                  FilledButton(onPressed: _busy ? null : _login, child: _busy ? const SizedBox(height: 22, width: 22, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : Text(_registering ? 'Create account' : 'Sign in')),
                  TextButton(onPressed: _busy ? null : () => setState(() { _registering = !_registering; _error = null; }), child: Center(child: Text(_registering ? 'Already have an account? Sign in' : 'New to FamilyRoots? Create an account'))),
                  const SizedBox(height: 18),
                  const Center(child: Text('Your family story belongs to you.', style: TextStyle(color: Colors.black54))),
                  const SizedBox(height: 12),
                  const Center(child: Icon(Icons.eco_outlined, color: _gold)),
                ]),
              ),
            ),
          ),
        ),
      );
}

class CommunityScreen extends ConsumerStatefulWidget {
  const CommunityScreen({super.key});
  @override
  ConsumerState<CommunityScreen> createState() => _CommunityScreenState();
}

class _CommunityScreenState extends ConsumerState<CommunityScreen> {
  late Future<List<dynamic>> _communities;
  @override
  void initState() { super.initState(); _communities = ref.read(apiProvider).communities(); }

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: const Text('Your families'), actions: [IconButton(tooltip: 'Sign out', onPressed: () async { await _storage.delete(key: 'access_token'); if (context.mounted) Navigator.of(context).pushAndRemoveUntil(MaterialPageRoute(builder: (_) => const LoginScreen()), (_) => false); }, icon: const Icon(Icons.logout))]),
        body: FutureBuilder<List<dynamic>>(
          future: _communities,
          builder: (context, snapshot) {
            if (snapshot.connectionState != ConnectionState.done) return const Center(child: CircularProgressIndicator());
            if (snapshot.hasError) return Center(child: TextButton.icon(onPressed: () => setState(() => _communities = ref.read(apiProvider).communities()), icon: const Icon(Icons.refresh), label: const Text('Could not load families. Try again.')));
            final communities = snapshot.data ?? [];
            if (communities.isEmpty) return const Center(child: Padding(padding: EdgeInsets.all(32), child: Text('You have no family communities yet. Ask a community owner to invite you.')));
            return ListView.separated(padding: const EdgeInsets.all(20), itemCount: communities.length, separatorBuilder: (_, __) => const SizedBox(height: 12), itemBuilder: (context, i) {
              final c = communities[i] as Map<String, dynamic>;
              return Card(child: ListTile(leading: const CircleAvatar(backgroundColor: Color(0xFFE5ECE6), child: Icon(Icons.account_tree, color: _green)), title: Text(c['name'] as String), subtitle: Text(c['description'] as String? ?? 'Family community'), trailing: const Icon(Icons.chevron_right), onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => TreeScreen(community: c)))));
            });
          },
        ),
      );
}

class TreeScreen extends ConsumerWidget {
  const TreeScreen({required this.community, super.key});
  final Map<String, dynamic> community;
  @override
  Widget build(BuildContext context, WidgetRef ref) => Scaffold(
        appBar: AppBar(title: Text(community['name'] as String)),
        body: FutureBuilder<List<dynamic>>(
          future: ref.read(apiProvider).people(community['id'] as String),
          builder: (context, snapshot) {
            if (snapshot.connectionState != ConnectionState.done) return const Center(child: CircularProgressIndicator());
            if (snapshot.hasError) return const Center(child: Text('Could not load family members.'));
            final people = snapshot.data ?? [];
            if (people.isEmpty) return const Center(child: Text('This family tree is ready for its first story.'));
            return InteractiveViewer(minScale: .5, maxScale: 3, child: Center(child: Wrap(alignment: WrapAlignment.center, spacing: 18, runSpacing: 24, children: [for (final p in people) _PersonCard(person: p as Map<String, dynamic>)])));
          },
        ),
      );
}

class _PersonCard extends StatelessWidget {
  const _PersonCard({required this.person});
  final Map<String, dynamic> person;
  @override
  Widget build(BuildContext context) => SizedBox(width: 165, child: Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(children: [const CircleAvatar(backgroundColor: Color(0xFFE5ECE6), child: Icon(Icons.person_outline, color: _green)), const SizedBox(height: 10), Text(person['display_name'] as String, textAlign: TextAlign.center, style: const TextStyle(fontWeight: FontWeight.w600)), if (person['birth_place'] != null) Text(person['birth_place'] as String, maxLines: 1, overflow: TextOverflow.ellipsis, style: Theme.of(context).textTheme.bodySmall)]))));
}
