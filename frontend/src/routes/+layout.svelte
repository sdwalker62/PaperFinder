<script lang="ts">
	import Navbar from "$lib/components/Navbar.svelte";
	import "../app.css";

	let { children } = $props();
</script>

<svelte:head>
	<title>PaperFinder</title>
	<meta name="description" content="Daily AI/ML paper and blog digest" />
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
	<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Lora:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet" />
</svelte:head>

<div class="min-h-screen bg-base-100 text-base-content">
	<Navbar />
	<main class="container mx-auto max-w-4xl px-4 py-8">
		{@render children()}
	</main>
</div>
